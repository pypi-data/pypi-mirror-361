# -*- coding: utf-8 -*-
# file: model.py
# author: YANG, HENG <hy345@exeter.ac.uk> (杨恒)
# github: https://github.com/yangheng95
# huggingface: https://huggingface.co/yangheng
# google scholar: https://scholar.google.com/citations?user=NPq5a_0AAAAJ&hl=en
# Copyright (C) 2019-2024. All Rights Reserved.
"""
RNA design model using masked language modeling and evolutionary algorithms.

This module provides an RNA design model that combines masked language modeling
with evolutionary algorithms to design RNA sequences that fold into specific
target structures. It uses a multi-objective optimization approach to balance
structure similarity and thermodynamic stability.
"""
import random
import numpy as np
import torch
import autocuda
from transformers import AutoModelForMaskedLM, AutoTokenizer
from concurrent.futures import ProcessPoolExecutor
import ViennaRNA
from scipy.spatial.distance import hamming

from omnigenome.src.misc.utils import fprint


class OmniModelForRNADesign(torch.nn.Module):
    """
    RNA design model using masked language modeling and evolutionary algorithms.
    
    This model combines a pre-trained masked language model with evolutionary
    algorithms to design RNA sequences that fold into specific target structures.
    It uses a multi-objective optimization approach to balance structure similarity
    and thermodynamic stability.
    
    Attributes:
        device: Device to run the model on (CPU or GPU)
        parallel: Whether to use parallel processing for structure prediction
        tokenizer: Tokenizer for processing RNA sequences
        model: Pre-trained masked language model
    """
    
    def __init__(
        self,
        model="yangheng/OmniGenome-186M",
        device=None,
        parallel=False,
        *args,
        **kwargs,
    ):
        """
        Initialize the RNA design model.
        
        Args:
            model (str): Model name or path for the pre-trained MLM model
            device: Device to run the model on (default: None, auto-detect)
            parallel (bool): Whether to use parallel processing (default: False)
            *args: Additional positional arguments
            **kwargs: Additional keyword arguments
        """
        super().__init__(*args, **kwargs)
        self.device = autocuda.auto_cuda() if device is None else device
        self.parallel = parallel
        self.tokenizer = AutoTokenizer.from_pretrained(model)
        self.model = AutoModelForMaskedLM.from_pretrained(model, trust_remote_code=True)
        self.model.to(self.device).to(torch.float16)

    @staticmethod
    def _random_bp_span(bp_span=None):
        """
        Generate a random base pair span.
        
        Args:
            bp_span (int, optional): Base pair span to center around (default: None)
            
        Returns:
            int: Random base pair span within ±50 of the input span
        """
        return random.choice(range(max(0, bp_span - 50), min(bp_span + 50, 400)))

    @staticmethod
    def _longest_bp_span(structure):
        """
        Compute the longest base-pair span from RNA structure.
        
        Args:
            structure (str): RNA structure in dot-bracket notation
            
        Returns:
            int: Length of the longest base-pair span
        """
        stack = []
        max_span = 0
        for i, char in enumerate(structure):
            if char == "(":
                stack.append(i)
            elif char == ")" and stack:
                left_index = stack.pop()
                max_span = max(max_span, i - left_index)
        return max_span

    @staticmethod
    def _predict_structure_single(sequence, bp_span=-1):
        """
        Predict the RNA structure and minimum free energy (MFE) for a single sequence.
        
        Args:
            sequence (str): RNA sequence
            bp_span (int): Maximum base pair span for folding (default: -1, no limit)
            
        Returns:
            tuple: (structure, mfe) where structure is in dot-bracket notation
        """
        md = ViennaRNA.md()
        md.max_bp_span = bp_span
        fc = ViennaRNA.fold_compound(sequence, md)
        return fc.mfe()

    def _predict_structure(self, sequences, bp_span=-1):
        """
        Predict RNA structures for multiple sequences.
        
        Args:
            sequences (list): List of RNA sequences
            bp_span (int): Maximum base pair span for folding (default: -1, no limit)
            
        Returns:
            list: List of (structure, mfe) tuples
        """
        return [self._predict_structure_single(seq, bp_span) for seq in sequences]

    def _init_population(self, structure, num_population):
        """
        Initialize the population with masked sequences.
        
        Args:
            structure (str): Target RNA structure in dot-bracket notation
            num_population (int): Number of individuals in the population
            
        Returns:
            list: List of (sequence, bp_span) tuples representing the initial population
        """
        population = []
        mlm_inputs = []
        for _ in range(num_population):
            masked_sequence = "".join(
                [random.choice(["G", "C", "<mask>"]) for _ in structure]
            )
            mlm_inputs.append(f"{masked_sequence}<eos>{structure}")

        outputs = self._mlm_predict(mlm_inputs, structure)

        for i, output in enumerate(outputs):
            sequence = self.tokenizer.convert_ids_to_tokens(output.tolist())
            fixed_sequence = [
                x if x in "AGCT" else random.choice(["A", "T", "G", "C"])
                for x in sequence
            ]
            bp_span = self._random_bp_span(len(structure))
            population.append(("".join(fixed_sequence), bp_span))

        return population

    def _mlm_mutate(self, population, structure, mutation_ratio):
        """
        Apply mutation to the population using the masked language model (MLM).
        
        Args:
            population (list): Current population of (sequence, bp_span) tuples
            structure (str): Target RNA structure
            mutation_ratio (float): Ratio of tokens to mutate
            
        Returns:
            list: Mutated population of (sequence, bp_span) tuples
        """

        def mutate(sequence, mutation_rate):
            sequence = np.array(list(sequence))
            masked_indices = np.random.rand(len(sequence)) < mutation_rate
            sequence[masked_indices] = "$"
            return "".join(sequence).replace("$", "<mask>")

        mlm_inputs = []
        for sequence, bp_span in population:
            masked_sequence = mutate(sequence, mutation_ratio)
            mlm_inputs.append(f"{masked_sequence}<eos>{structure}")

        outputs = self._mlm_predict(mlm_inputs, structure)

        mut_population = []
        for i, (seq, bp_span) in enumerate(population):
            sequence = self.tokenizer.convert_ids_to_tokens(outputs[i].tolist())
            fixed_sequence = [
                x if x in "AGCT" else random.choice(["A", "T", "G", "C"])
                for x in sequence
            ]
            bp_span = self._random_bp_span(bp_span)
            mut_population.append(("".join(fixed_sequence), bp_span))

        return mut_population

    def _crossover(self, population, num_points=3):
        """
        Perform crossover operation to create offspring.
        
        Args:
            population (list): Current population of (sequence, bp_span) tuples
            num_points (int): Number of crossover points (default: 3)
            
        Returns:
            list: Offspring population after crossover
        """
        population_size = len(population)
        sequence_length = len(population[0][0])

        parent_indices = np.random.choice(population_size // 10, (population_size, 2))
        crossover_points = np.sort(
            np.random.randint(1, sequence_length, size=(population_size, num_points)),
            axis=1,
        )

        masks = np.zeros((population_size, sequence_length), dtype=bool)
        for i in range(population_size):
            last_point = 0
            for j in range(num_points):
                masks[i, last_point : crossover_points[i, j]] = j % 2 == 0
                last_point = crossover_points[i, j]
            masks[i, last_point:] = num_points % 2 == 0

        population_array = np.array([list(seq[0]) for seq in population])
        child1_array = np.where(
            masks,
            population_array[parent_indices[:, 0]],
            population_array[parent_indices[:, 1]],
        )
        child2_array = np.where(
            masks,
            population_array[parent_indices[:, 1]],
            population_array[parent_indices[:, 0]],
        )

        return [
            ("".join(child), bp_span)
            for child, (_, bp_span) in zip(child1_array, population)
        ] + [
            ("".join(child), bp_span)
            for child, (_, bp_span) in zip(child2_array, population)
        ]

    def _evaluate_structure_fitness(self, sequences, structure):
        """
        Evaluate the fitness of the RNA structure by comparing with the target structure.
        
        Args:
            sequences (list): List of (sequence, bp_span) tuples to evaluate
            structure (str): Target RNA structure
            
        Returns:
            list: Sorted population with fitness scores and MFE values
        """
        if self.parallel:
            with ProcessPoolExecutor() as executor:
                structures_mfe = list(
                    executor.map(
                        self._predict_structure_single, [seq for seq, _ in sequences]
                    )
                )
        else:
            structures_mfe = self._predict_structure([seq for seq, _ in sequences])

        sorted_population = []
        for (seq, bp_span), (ss, mfe) in zip(sequences, structures_mfe):
            score = hamming(list(structure), list(ss))
            sorted_population.append((seq, bp_span, score, mfe))

        fronts = self._non_dominated_sorting(
            [x[2] for x in sorted_population], [x[3] for x in sorted_population]
        )
        return self._select_next_generation(sorted_population, fronts)

    @staticmethod
    def _non_dominated_sorting(scores, mfe_values):
        """
        Perform non-dominated sorting for multi-objective optimization.
        
        Args:
            scores (list): Structure similarity scores
            mfe_values (list): Minimum free energy values
            
        Returns:
            list: List of fronts (Pareto fronts)
        """
        num_solutions = len(scores)
        domination_count = [0] * num_solutions
        dominated_solutions = [[] for _ in range(num_solutions)]
        fronts = [[]]

        for p in range(num_solutions):
            for q in range(num_solutions):
                if scores[p] < scores[q] and mfe_values[p] < mfe_values[q]:
                    dominated_solutions[p].append(q)
                elif scores[q] < scores[p] and mfe_values[q] < mfe_values[p]:
                    domination_count[p] += 1

            if domination_count[p] == 0:
                fronts[0].append(p)

        i = 0
        while len(fronts[i]) > 0:
            next_front = []
            for p in fronts[i]:
                for q in dominated_solutions[p]:
                    domination_count[q] -= 1
                    if domination_count[q] == 0:
                        next_front.append(q)
            i += 1
            fronts.append(next_front)

        if not fronts[-1]:  # Ensure the last front is not empty before removing
            fronts.pop(-1)

        return fronts

    @staticmethod
    def _select_next_generation(next_generation, fronts):
        """
        Select the next generation based on Pareto fronts.
        
        Args:
            next_generation (list): Current population with fitness scores
            fronts (list): Pareto fronts
            
        Returns:
            list: Selected population for the next generation
        """
        sorted_population = []
        for front in fronts:
            front_population = [next_generation[i] for i in front]
            sorted_population.extend(front_population)
            if len(sorted_population) >= len(next_generation):
                break

        return sorted_population[: len(next_generation)]

    def _mlm_predict(self, mlm_inputs, structure):
        """
        Perform masked language model prediction.
        
        Args:
            mlm_inputs (list): List of masked input sequences
            structure (str): Target RNA structure
            
        Returns:
            list: Predicted token IDs for each input
        """
        batch_size = 8
        all_outputs = []

        with torch.no_grad():
            for i in range(0, len(mlm_inputs), batch_size):
                inputs = self.tokenizer(
                    mlm_inputs[i: i + batch_size],
                    padding=False,
                    max_length=1024,
                    truncation=True,
                    return_tensors="pt",
                )
                inputs = {
                    key: value.to(self.model.device) for key, value in inputs.items()
                }
                outputs = self.model(**inputs)[0].argmax(dim=-1)
                all_outputs.append(outputs)

        return torch.cat(all_outputs, dim=0)[:, 1 : 1 + len(structure)]

    def design(
        self, structure, mutation_ratio=0.5, num_population=100, num_generation=100
    ):
        """
        Design RNA sequences for a target structure using evolutionary algorithms.
        
        Args:
            structure (str): Target RNA structure in dot-bracket notation
            mutation_ratio (float): Ratio of tokens to mutate (default: 0.5)
            num_population (int): Population size (default: 100)
            num_generation (int): Number of generations (default: 100)
            
        Returns:
            list: List of designed RNA sequences with their fitness scores
        """
        population = self._init_population(structure, num_population)
        population = self._mlm_mutate(population, structure, mutation_ratio)

        for generation_id in range(num_generation):
            next_generation = self._crossover(population)
            next_generation = self._mlm_mutate(
                next_generation, structure, mutation_ratio
            )
            next_generation = self._evaluate_structure_fitness(
                next_generation, structure
            )[:num_population]

            candidate_sequences = [
                seq for seq, bp_span, score, mfe in next_generation if score == 0
            ]
            if candidate_sequences:
                return candidate_sequences

            population = [
                (seq, bp_span) for seq, bp_span, score, mfe in next_generation
            ]

        return population[0][0]


# Example usage
if __name__ == "__main__":
    model = OmniModelForRNADesign(model="anonymous8/OmniGenome-186M")
    best_sequence = model.design(
        structure="(((....)))",
        mutation_ratio=0.5,
        num_population=100,
        num_generation=100,
    )
    fprint(f"Best RNA sequence: {best_sequence}")
