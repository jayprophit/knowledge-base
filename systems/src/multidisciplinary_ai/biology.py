"""
Biology Module
=============

Implements biological systems, processes, and evolutionary principles.
"""

from typing import Dict, Any, List, Optional, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum, auto
import random
import math
from collections import defaultdict
import numpy as np

class OrganismType(Enum):
    """Types of organisms."""
    PLANT = "plant"
    ANIMAL = "animal"
    FUNGUS = "fungus"
    BACTERIA = "bacteria"
    ARCHAEON = "archaeon"
    PROTIST = "protist"

class LifeStage(Enum):
    """Life stages of an organism."""
    EMBRYONIC = "embryonic"
    JUVENILE = "juvenile"
    ADULT = "adult"
    SENESCENT = "senescent"

class EcosystemType(Enum):
    """Types of ecosystems."""
    FOREST = "forest"
    GRASSLAND = "grassland"
    DESERT = "desert"
    TUNDRA = "tundra"
    FRESHWATER = "freshwater"
    MARINE = "marine"
    URBAN = "urban"
    AGRICULTURAL = "agricultural"

@dataclass
class Gene:
    """Represents a gene with its alleles and expression."""
    name: str
    alleles: List[str]  # Different versions of the gene
    dominant_allele: Optional[str] = None  # Which allele is dominant
    expression_level: float = 1.0  # How strongly the gene is expressed (0-1)

@dataclass
class Organism:
    """Represents a biological organism."""
    organism_id: str
    organism_type: OrganismType
    species: str
    genes: Dict[str, Gene]  # Gene name -> Gene object
    traits: Dict[str, Any]  # Observable characteristics
    position: Tuple[float, float] = (0.0, 0.0)  # Position in the environment
    energy: float = 100.0  # Energy level (0 = death)
    age: int = 0  # Age in time steps
    life_stage: LifeStage = LifeStage.JUVENILE
    max_age: int = 1000  # Maximum possible age
    reproduction_threshold: float = 150.0  # Energy needed to reproduce
    
    def update(self, environment: 'Ecosystem') -> List['Organism']:
        """
        Update the organism's state based on the environment.
        
        Args:
            environment: The ecosystem the organism is in
            
        Returns:
            List of new organisms if reproduction occurred
        """
        self.age += 1
        self.energy -= 1  # Base metabolism
        
        # Update life stage
        if self.age < self.max_age * 0.1:
            self.life_stage = LifeStage.JUVENILE
        elif self.age < self.max_age * 0.8:
            self.life_stage = LifeStage.ADULT
        else:
            self.life_stage = LifeStage.SENESCENT
        
        # Senescence effects
        if self.life_stage == LifeStage.SENESCENT:
            self.energy *= 0.95  # Reduced efficiency
        
        # Check for death
        if self.energy <= 0 or self.age >= self.max_age:
            return []
        
        # Try to find food
        self._forage(environment)
        
        # Try to reproduce if conditions are right
        offspring = []
        if (self.energy > self.reproduction_threshold and 
            self.life_stage == LifeStage.ADULT):
            offspring = self._reproduce()
        
        return offspring
    
    def _forage(self, environment: 'Ecosystem') -> None:
        """Find and consume food in the environment."""
        # Simple foraging behavior - in a real simulation, this would be more complex
        food_found = environment.find_food(self.position, self.traits.get('foraging_radius', 1.0))
        
        if food_found:
            # Consume food and gain energy
            food_value = food_found['value']
            self.energy = min(self.energy + food_value, self.traits.get('max_energy', 200.0))
            environment.remove_food(food_found['id'])
    
    def _reproduce(self) -> List['Organism']:
        """Create offspring through reproduction."""
        offspring = []
        # Simple reproduction - in a real simulation, this would involve two parents
        # and genetic recombination
        if random.random() < 0.3:  # 30% chance of reproduction attempt
            child_genes = {}
            for gene_name, gene in self.genes.items():
                # Simple inheritance - randomly select one allele from parent
                child_allele = random.choice(gene.alleles)
                child_genes[gene_name] = Gene(
                    name=gene.name,
                    alleles=[child_allele],
                    dominant_allele=gene.dominant_allele,
                    expression_level=gene.expression_level * random.uniform(0.9, 1.1)
                )
            
            child = Organism(
                organism_id=f"{self.organism_id}_child_{random.randint(0, 1000)}",
                organism_type=self.organism_type,
                species=self.species,
                genes=child_genes,
                traits=self._calculate_traits(child_genes),
                position=(self.position[0] + random.uniform(-1, 1), 
                         self.position[1] + random.uniform(-1, 1)),
                energy=self.energy * 0.5  # Parent invests energy in offspring
            )
            
            self.energy *= 0.5  # Reproduction costs energy
            offspring.append(child)
        
        return offspring
    
    def _calculate_traits(self, genes: Dict[str, Gene]) -> Dict[str, Any]:
        """Calculate observable traits from genes."""
        traits = {}
        
        # In a real implementation, this would be a complex mapping from
        # genotype to phenotype, possibly involving epistasis, pleiotropy, etc.
        
        # Simple example: size trait
        if 'size_gene' in genes:
            size_allele = genes['size_gene'].alleles[0]
            traits['size'] = 1.0 if size_allele == 'L' else 0.5
        
        # Add more trait calculations as needed
        
        return traits

@dataclass
class FoodSource:
    """Represents a source of food in the ecosystem."""
    food_id: str
    position: Tuple[float, float]
    value: float  # Energy value
    regrowth_rate: float = 0.1  # How quickly the food source regenerates
    current_value: float = field(init=False)
    
    def __post_init__(self):
        self.current_value = self.value
    
    def consume(self, amount: float) -> float:
        """Consume some amount of the food source."""
        consumed = min(amount, self.current_value)
        self.current_value -= consumed
        return consumed
    
    def update(self) -> None:
        """Regrow the food source."""
        self.current_value = min(
            self.value,
            self.current_value + self.value * self.regrowth_rate
        )

class Ecosystem:
    """
    Represents an ecosystem containing organisms and their environment.
    """
    
    def __init__(self, 
                 ecosystem_type: EcosystemType = EcosystemType.FOREST,
                 size: Tuple[int, int] = (100, 100)):
        """
        Initialize the ecosystem.
        
        Args:
            ecosystem_type: Type of ecosystem
            size: Size of the ecosystem (width, height)
        """
        self.ecosystem_type = ecosystem_type
        self.size = size
        self.organisms: List[Organism] = []
        self.food_sources: Dict[str, FoodSource] = {}
        self.time_step = 0
        self.history = []
        
        # Initialize with some organisms and food
        self._initialize_ecosystem()
    
    def _initialize_ecosystem(self) -> None:
        """Initialize the ecosystem with organisms and food sources."""
        # Add some food sources
        for i in range(20):
            food_id = f"food_{i}"
            self.food_sources[food_id] = FoodSource(
                food_id=food_id,
                position=(
                    random.uniform(0, self.size[0]),
                    random.uniform(0, self.size[1])
                ),
                value=random.uniform(10, 50),
                regrowth_rate=random.uniform(0.05, 0.2)
            )
        
        # Add some organisms
        for i in range(10):
            org_type = random.choice(list(OrganismType))
            species = f"species_{random.randint(1, 5)}"
            
            # Create some genes
            genes = {
                'size_gene': Gene(
                    name='size_gene',
                    alleles=['L' if random.random() > 0.5 else 'S'],
                    dominant_allele='L',
                    expression_level=1.0
                )
                # Add more genes as needed
            }
            
            organism = Organism(
                organism_id=f"org_{i}",
                organism_type=org_type,
                species=species,
                genes=genes,
                traits={
                    'foraging_radius': random.uniform(1.0, 5.0),
                    'max_energy': random.uniform(150.0, 250.0)
                },
                position=(
                    random.uniform(0, self.size[0]),
                    random.uniform(0, self.size[1])
                ),
                energy=random.uniform(50.0, 150.0),
                age=random.randint(0, 500),
                max_age=random.randint(800, 1200)
            )
            
            self.organisms.append(organism)
    
    def update(self) -> None:
        """Update the ecosystem by one time step."""
        self.time_step += 1
        new_organisms = []
        
        # Update all organisms
        for org in self.organisms[:]:  # Make a copy for safe removal
            # Let the organism act
            offspring = org.update(self)
            
            # Add any new offspring
            if offspring:
                new_organisms.extend(offspring)
            
            # Remove dead organisms
            if org.energy <= 0 or org.age >= org.max_age:
                self.organisms.remove(org)
        
        # Add new organisms
        self.organisms.extend(new_organisms)
        
        # Update food sources
        for food in self.food_sources.values():
            food.update()
        
        # Record ecosystem state
        self._record_state()
    
    def find_food(self, position: Tuple[float, float], radius: float) -> Optional[Dict]:
        """
        Find food near a position within a given radius.
        
        Args:
            position: (x, y) position to search around
            radius: Search radius
            
        Returns:
            Food source information if found, None otherwise
        """
        closest_food = None
        min_dist = float('inf')
        
        for food in self.food_sources.values():
            if food.current_value <= 0:
                continue
                
            dist = math.sqrt(
                (position[0] - food.position[0])**2 + 
                (position[1] - food.position[1])**2
            )
            
            if dist <= radius and dist < min_dist:
                min_dist = dist
                closest_food = {
                    'id': food.food_id,
                    'position': food.position,
                    'value': food.current_value,
                    'distance': dist
                }
        
        return closest_food
    
    def remove_food(self, food_id: str) -> None:
        """Remove a food source (when consumed)."""
        if food_id in self.food_sources:
            self.food_sources[food_id].current_value = 0
    
    def _record_state(self) -> None:
        """Record the current state of the ecosystem."""
        state = {
            'time_step': self.time_step,
            'organism_count': len(self.organisms),
            'species_distribution': {},
            'total_biomass': sum(org.energy for org in self.organisms),
            'food_availability': sum(food.current_value for food in self.food_sources.values())
        }
        
        # Count organisms by species
        species_counts = defaultdict(int)
        for org in self.organisms:
            species_counts[org.species] += 1
        
        state['species_distribution'] = dict(species_counts)
        self.history.append(state)
        
        # Keep history manageable
        if len(self.history) > 1000:
            self.history = self.history[-1000:]
    
    def get_ecosystem_metrics(self) -> Dict[str, Any]:
        """
        Calculate various metrics about the ecosystem.
        
        Returns:
            Dictionary of ecosystem metrics
        """
        if not self.history:
            return {}
        
        current = self.history[-1]
        metrics = {
            'time_step': current['time_step'],
            'organism_count': current['organism_count'],
            'species_richness': len(current['species_distribution']),
            'species_diversity': self._calculate_species_diversity(current['species_distribution']),
            'food_availability': current['food_availability'],
            'total_biomass': current['total_biomass'],
            'trend': self._calculate_trends()
        }
        
        return metrics
    
    def _calculate_species_diversity(self, species_dist: Dict[str, int]) -> float:
        """Calculate Shannon diversity index."""
        total = sum(species_dist.values())
        if total == 0:
            return 0.0
        
        proportions = [count / total for count in species_dist.values()]
        return -sum(p * math.log(p) for p in proportions if p > 0)
    
    def _calculate_trends(self) -> Dict[str, str]:
        """Calculate trends in the ecosystem."""
        if len(self.history) < 2:
            return {"status": "Insufficient data for trend analysis"}
        
        current = self.history[-1]
        prev = self.history[-2]
        
        trends = {}
        
        # Population trend
        pop_change = current['organism_count'] - prev['organism_count']
        if pop_change > 0:
            trends['population'] = f"Increasing (+{pop_change})"
        elif pop_change < 0:
            trends['population'] = f"Decreasing ({pop_change})"
        else:
            trends['population'] = "Stable"
        
        # Species richness trend
        richness_change = len(current['species_distribution']) - len(prev['species_distribution'])
        if richness_change > 0:
            trends['species_richness'] = f"Increasing (+{richness_change})"
        elif richness_change < 0:
            trends['species_richness'] = f"Decreasing ({richness_change})"
        else:
            trends['species_richness'] = "Stable"
        
        # Food availability trend
        food_change = current['food_availability'] - prev['food_availability']
        if food_change > 0:
            trends['food_availability'] = f"Increasing (+{food_change:.1f})"
        elif food_change < 0:
            trends['food_availability'] = f"Decreasing ({food_change:.1f})"
        else:
            trends['food_availability'] = "Stable"
        
        return trends

class BiologyModule:
    """
    Main module for biological simulations and analysis.
    """
    
    def __init__(self):
        """Initialize the biology module."""
        self.ecosystems: Dict[str, Ecosystem] = {}
        self.species_database = {}
        self.genetic_models = {}
    
    def create_ecosystem(self, 
                        ecosystem_id: str, 
                        ecosystem_type: EcosystemType = EcosystemType.FOREST,
                        size: Tuple[int, int] = (100, 100)) -> Dict[str, Any]:
        """
        Create a new ecosystem.
        
        Args:
            ecosystem_id: Unique identifier for the ecosystem
            ecosystem_type: Type of ecosystem
            size: Size of the ecosystem (width, height)
            
        Returns:
            Status of the operation
        """
        if ecosystem_id in self.ecosystems:
            return {"status": "error", "message": f"Ecosystem {ecosystem_id} already exists"}
        
        self.ecosystems[ecosystem_id] = Ecosystem(ecosystem_type, size)
        return {
            "status": "success", 
            "message": f"Created {ecosystem_type.value} ecosystem {ecosystem_id}"
        }
    
    def simulate_ecosystem(self, 
                          ecosystem_id: str, 
                          steps: int = 1) -> Dict[str, Any]:
        """
        Simulate an ecosystem for a number of time steps.
        
        Args:
            ecosystem_id: ID of the ecosystem to simulate
            steps: Number of time steps to simulate
            
        Returns:
            Simulation results
        """
        if ecosystem_id not in self.ecosystems:
            return {"status": "error", "message": f"Ecosystem {ecosystem_id} not found"}
        
        ecosystem = self.ecosystems[ecosystem_id]
        
        for _ in range(steps):
            ecosystem.update()
        
        metrics = ecosystem.get_ecosystem_metrics()
        return {
            "status": "success",
            "steps_simulated": steps,
            "current_time_step": ecosystem.time_step,
            "metrics": metrics
        }
    
    def get_ecosystem_state(self, 
                           ecosystem_id: str, 
                           include_history: bool = False) -> Dict[str, Any]:
        """
        Get the current state of an ecosystem.
        
        Args:
            ecosystem_id: ID of the ecosystem
            include_history: Whether to include historical data
            
        Returns:
            Current state of the ecosystem
        """
        if ecosystem_id not in self.ecosystems:
            return {"status": "error", "message": f"Ecosystem {ecosystem_id} not found"}
        
        ecosystem = self.ecosystems[ecosystem_id]
        state = {
            "ecosystem_id": ecosystem_id,
            "ecosystem_type": ecosystem.ecosystem_type.value,
            "size": ecosystem.size,
            "current_time_step": ecosystem.time_step,
            "metrics": ecosystem.get_ecosystem_metrics()
        }
        
        if include_history and ecosystem.history:
            state["history"] = ecosystem.history
        
        return state
    
    def analyze_genetic_data(self, 
                           genetic_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze genetic data.
        
        Args:
            genetic_data: Dictionary containing genetic data
            
        Returns:
            Analysis results
        """
        # In a real implementation, this would perform actual genetic analysis
        # For now, we'll return a placeholder analysis
        
        # Count alleles
        allele_counts = {}
        for gene_name, gene_data in genetic_data.get('genes', {}).items():
            allele_counts[gene_name] = {}
            for allele in gene_data.get('alleles', []):
                if allele in allele_counts[gene_name]:
                    allele_counts[gene_name][allele] += 1
                else:
                    allele_counts[gene_name][allele] = 1
        
        # Calculate allele frequencies
        allele_frequencies = {}
        for gene_name, counts in allele_counts.items():
            total = sum(counts.values())
            allele_frequencies[gene_name] = {
                allele: count / total 
                for allele, count in counts.items()
            }
        
        # Check for Hardy-Weinberg equilibrium (simplified)
        hw_violations = []
        for gene_name, freqs in allele_frequencies.items():
            if len(freqs) == 2:  # Only check for biallelic loci
                p = list(freqs.values())[0]
                q = 1 - p
                expected_het = 2 * p * q
                observed_het = genetic_data.get('observed_heterozygosity', {}).get(gene_name, 0)
                
                if abs(expected_het - observed_het) > 0.1:  # Arbitrary threshold
                    hw_violations.append(gene_name)
        
        return {
            'allele_frequencies': allele_frequencies,
            'hardy_weinberg_violations': hw_violations,
            'genetic_diversity': self._calculate_genetic_diversity(allele_frequencies),
            'inbreeding_coefficient': random.uniform(0, 0.1)  # Placeholder
        }
    
    def _calculate_genetic_diversity(self, 
                                   allele_frequencies: Dict[str, Dict[str, float]]) -> float:
        """Calculate average expected heterozygosity across loci."""
        if not allele_frequencies:
            return 0.0
        
        het_sum = 0.0
        for freqs in allele_frequencies.values():
            het = 1 - sum(freq**2 for freq in freqs.values())
            het_sum += het
        
        return het_sum / len(allele_frequencies)
    
    def analyze(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main analysis method that processes biological input data.
        
        Args:
            input_data: Dictionary containing 'ecosystem', 'genetics', or 'species' data
            
        Returns:
            Analysis results including ecosystem simulation or genetic analysis
        """
        result = {}
        
        # Handle ecosystem simulation
        if 'ecosystem' in input_data:
            ecosystem_data = input_data['ecosystem']
            action = ecosystem_data.get('action')
            
            if action == 'create':
                ecosystem_id = ecosystem_data.get('id', 'default')
                ecosystem_type = EcosystemType(ecosystem_data.get('type', 'forest'))
                size = tuple(ecosystem_data.get('size', [100, 100]))
                result['ecosystem'] = self.create_ecosystem(
                    ecosystem_id, ecosystem_type, size
                )
            
            elif action == 'simulate':
                ecosystem_id = ecosystem_data.get('id', 'default')
                steps = ecosystem_data.get('steps', 1)
                result['simulation'] = self.simulate_ecosystem(ecosystem_id, steps)
            
            elif action == 'get_state':
                ecosystem_id = ecosystem_data.get('id', 'default')
                include_history = ecosystem_data.get('include_history', False)
                result['ecosystem_state'] = self.get_ecosystem_state(
                    ecosystem_id, include_history
                )
        
        # Handle genetic analysis
        if 'genetics' in input_data:
            result['genetic_analysis'] = self.analyze_genetic_data(
                input_data['genetics']
            )
        
        # Handle species data
        if 'species' in input_data:
            # In a real implementation, this would query a species database
            result['species_info'] = {
                'status': 'not_implemented',
                'message': 'Species database query not implemented'
            }
        
        return result
