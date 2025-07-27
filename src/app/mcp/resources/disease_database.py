"""
Disease Database MCP Resource

Provides comprehensive crop disease information and management strategies
through the MCP interface.
"""

import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


class DiseaseDatabaseResource:
    """
    MCP resource for crop disease database.

    Provides comprehensive information about common crop diseases,
    their symptoms, causes, and management strategies.
    """

    def __init__(self):
        self.disease_data = self._initialize_disease_database()

    async def get_database(self) -> Dict[str, Any]:
        """
        Get the complete crop disease database.

        Returns:
            Comprehensive disease database with management information
        """
        try:
            database_response = {
                "status": "success",
                "database_info": {
                    "total_diseases": len(self.disease_data["diseases"]),
                    "crops_covered": list(
                        set(
                            crop
                            for disease in self.disease_data["diseases"].values()
                            for crop in disease.get("affected_crops", [])
                        )
                    ),
                    "disease_categories": list(self.disease_data["categories"].keys()),
                    "last_updated": "2025-01-27",
                },
                "categories": self.disease_data["categories"],
                "diseases": self.disease_data["diseases"],
                "prevention_strategies": self.disease_data["prevention_strategies"],
                "management_principles": self.disease_data["management_principles"],
                "diagnostic_guide": self.disease_data["diagnostic_guide"],
            }

            logger.info("Disease database retrieved successfully")
            return database_response

        except Exception as e:
            logger.error(f"Error retrieving disease database: {e}")
            return {
                "error": "database_retrieval_failed",
                "message": "Unable to retrieve disease database",
            }

    def _initialize_disease_database(self) -> Dict[str, Any]:
        """Initialize the comprehensive disease database."""
        return {
            "categories": {
                "fungal": {
                    "name": "Fungal Diseases",
                    "description": "Diseases caused by fungal pathogens",
                    "characteristics": [
                        "Thrive in warm, humid conditions",
                        "Often show visible fungal growth",
                        "Spread through spores",
                        "Can be soil-borne or air-borne",
                    ],
                    "common_symptoms": [
                        "Spots on leaves",
                        "Wilting",
                        "Rotting",
                        "Powdery growth",
                    ],
                },
                "bacterial": {
                    "name": "Bacterial Diseases",
                    "description": "Diseases caused by bacterial pathogens",
                    "characteristics": [
                        "Spread through water and insects",
                        "Often cause wilting and rotting",
                        "May produce bacterial ooze",
                        "Difficult to control once established",
                    ],
                    "common_symptoms": [
                        "Leaf spots",
                        "Wilting",
                        "Cankers",
                        "Bacterial ooze",
                    ],
                },
                "viral": {
                    "name": "Viral Diseases",
                    "description": "Diseases caused by viral pathogens",
                    "characteristics": [
                        "Transmitted by insects or mechanical means",
                        "Cause systemic infections",
                        "No direct chemical control",
                        "Prevention is key",
                    ],
                    "common_symptoms": [
                        "Mosaic patterns",
                        "Stunting",
                        "Yellowing",
                        "Deformation",
                    ],
                },
                "nematode": {
                    "name": "Nematode Diseases",
                    "description": "Diseases caused by plant-parasitic nematodes",
                    "characteristics": [
                        "Microscopic roundworms",
                        "Attack roots primarily",
                        "Cause nutrient deficiency symptoms",
                        "Soil-borne pathogens",
                    ],
                    "common_symptoms": [
                        "Root galls",
                        "Stunting",
                        "Yellowing",
                        "Poor growth",
                    ],
                },
            },
            "diseases": {
                "rice_blast": {
                    "name": "Rice Blast",
                    "scientific_name": "Magnaporthe oryzae",
                    "category": "fungal",
                    "affected_crops": ["Rice"],
                    "severity": "High",
                    "symptoms": {
                        "leaf_symptoms": [
                            "Diamond-shaped lesions with gray centers",
                            "Brown borders around lesions",
                            "Lesions may coalesce causing leaf death",
                        ],
                        "neck_symptoms": [
                            "Brown to black lesions on neck",
                            "Panicle may break at infected point",
                            "Incomplete grain filling",
                        ],
                        "panicle_symptoms": [
                            "Brown discoloration of panicle branches",
                            "Poor grain filling",
                            "Chaffy grains",
                        ],
                    },
                    "favorable_conditions": {
                        "temperature": "26-28°C",
                        "humidity": ">90%",
                        "other_factors": [
                            "High nitrogen",
                            "Dense planting",
                            "Prolonged leaf wetness",
                        ],
                    },
                    "management": {
                        "cultural": [
                            "Use resistant varieties",
                            "Balanced fertilization",
                            "Proper spacing",
                            "Remove infected debris",
                        ],
                        "chemical": [
                            "Tricyclazole 75% WP @ 0.6g/L",
                            "Propiconazole 25% EC @ 1ml/L",
                            "Azoxystrobin 23% SC @ 1ml/L",
                        ],
                        "biological": ["Trichoderma viride", "Pseudomonas fluorescens"],
                    },
                    "economic_impact": "Can cause 10-50% yield loss",
                },
                "bacterial_leaf_blight": {
                    "name": "Bacterial Leaf Blight",
                    "scientific_name": "Xanthomonas oryzae pv. oryzae",
                    "category": "bacterial",
                    "affected_crops": ["Rice"],
                    "severity": "High",
                    "symptoms": {
                        "early_stage": [
                            "Water-soaked lesions near leaf tips",
                            "Yellow halos around lesions",
                            "Lesions extend along leaf veins",
                        ],
                        "advanced_stage": [
                            "Entire leaves turn yellow and die",
                            "Bacterial ooze in morning",
                            "Kresek symptom (wilting of young plants)",
                        ],
                    },
                    "favorable_conditions": {
                        "temperature": "25-30°C",
                        "humidity": "High humidity",
                        "other_factors": ["Wounds", "High nitrogen", "Flooding"],
                    },
                    "management": {
                        "cultural": [
                            "Use resistant varieties",
                            "Avoid excess nitrogen",
                            "Proper water management",
                            "Remove infected plants",
                        ],
                        "chemical": [
                            "Copper oxychloride 50% WP @ 3g/L",
                            "Streptomycin sulphate 90% + Tetracycline 10% @ 0.5g/L",
                        ],
                        "biological": ["Pseudomonas fluorescens", "Bacillus subtilis"],
                    },
                    "economic_impact": "Can cause 20-80% yield loss",
                },
                "cotton_bollworm": {
                    "name": "Cotton Bollworm",
                    "scientific_name": "Helicoverpa armigera",
                    "category": "insect_pest",
                    "affected_crops": ["Cotton", "Tomato", "Chickpea"],
                    "severity": "High",
                    "symptoms": {
                        "larval_damage": [
                            "Holes in leaves and bolls",
                            "Feeding on developing bolls",
                            "Frass (insect excrement) visible",
                        ],
                        "plant_response": [
                            "Reduced boll formation",
                            "Poor fiber quality",
                            "Yield reduction",
                        ],
                    },
                    "favorable_conditions": {
                        "temperature": "25-30°C",
                        "humidity": "Moderate humidity",
                        "other_factors": ["Flowering stage", "High nitrogen"],
                    },
                    "management": {
                        "cultural": [
                            "Crop rotation",
                            "Intercropping with marigold",
                            "Removal of alternate hosts",
                            "Deep plowing",
                        ],
                        "chemical": [
                            "Chlorantraniliprole 18.5% SC @ 0.3ml/L",
                            "Emamectin benzoate 5% SG @ 0.5g/L",
                            "Spinosad 45% SC @ 0.3ml/L",
                        ],
                        "biological": [
                            "NPV (Nuclear Polyhedrosis Virus)",
                            "Trichogramma parasitoids",
                            "Chrysoperla carnea",
                        ],
                    },
                    "economic_impact": "Can cause 30-60% yield loss",
                },
                "wheat_rust": {
                    "name": "Wheat Rust",
                    "scientific_name": "Puccinia triticina",
                    "category": "fungal",
                    "affected_crops": ["Wheat"],
                    "severity": "High",
                    "symptoms": {
                        "leaf_rust": [
                            "Orange-red pustules on leaves",
                            "Pustules scattered randomly",
                            "Leaves turn yellow and dry",
                        ],
                        "stem_rust": [
                            "Dark red pustules on stems",
                            "Stems become weak and break",
                            "Black spores in later stages",
                        ],
                    },
                    "favorable_conditions": {
                        "temperature": "15-25°C",
                        "humidity": "High humidity with dew",
                        "other_factors": ["Susceptible varieties", "Dense planting"],
                    },
                    "management": {
                        "cultural": [
                            "Use resistant varieties",
                            "Proper spacing",
                            "Balanced nutrition",
                            "Remove volunteer plants",
                        ],
                        "chemical": [
                            "Propiconazole 25% EC @ 1ml/L",
                            "Tebuconazole 25.9% EC @ 1ml/L",
                            "Mancozeb 75% WP @ 2.5g/L",
                        ],
                    },
                    "economic_impact": "Can cause 20-70% yield loss",
                },
                "tomato_late_blight": {
                    "name": "Tomato Late Blight",
                    "scientific_name": "Phytophthora infestans",
                    "category": "fungal",
                    "affected_crops": ["Tomato", "Potato"],
                    "severity": "Very High",
                    "symptoms": {
                        "leaf_symptoms": [
                            "Dark brown lesions with yellow halos",
                            "White fungal growth on leaf undersides",
                            "Rapid spread in cool, wet weather",
                        ],
                        "fruit_symptoms": [
                            "Brown, firm lesions on fruits",
                            "White fungal growth",
                            "Fruits become unmarketable",
                        ],
                    },
                    "favorable_conditions": {
                        "temperature": "15-20°C",
                        "humidity": ">90%",
                        "other_factors": ["Leaf wetness", "Poor air circulation"],
                    },
                    "management": {
                        "cultural": [
                            "Use resistant varieties",
                            "Improve air circulation",
                            "Avoid overhead irrigation",
                            "Remove infected plants",
                        ],
                        "chemical": [
                            "Metalaxyl + Mancozeb @ 2.5g/L",
                            "Cymoxanil + Mancozeb @ 2g/L",
                            "Copper oxychloride @ 3g/L",
                        ],
                    },
                    "economic_impact": "Can cause complete crop loss",
                },
            },
            "prevention_strategies": {
                "general_principles": [
                    "Use certified, disease-free seeds",
                    "Follow crop rotation practices",
                    "Maintain field sanitation",
                    "Implement integrated pest management",
                    "Monitor crops regularly",
                    "Use resistant varieties when available",
                ],
                "cultural_practices": {
                    "soil_management": [
                        "Maintain proper soil drainage",
                        "Avoid waterlogging",
                        "Practice deep plowing",
                        "Add organic matter",
                    ],
                    "crop_management": [
                        "Maintain proper plant spacing",
                        "Avoid excess nitrogen fertilization",
                        "Practice timely sowing",
                        "Remove crop residues",
                    ],
                    "water_management": [
                        "Use drip irrigation when possible",
                        "Avoid overhead watering",
                        "Irrigate early morning",
                        "Maintain proper drainage",
                    ],
                },
                "biological_control": [
                    "Encourage beneficial insects",
                    "Use biocontrol agents",
                    "Maintain biodiversity",
                    "Avoid broad-spectrum pesticides",
                ],
            },
            "management_principles": {
                "integrated_approach": [
                    "Combine multiple control methods",
                    "Prioritize prevention over cure",
                    "Use chemicals as last resort",
                    "Monitor and evaluate effectiveness",
                ],
                "resistance_management": [
                    "Rotate different chemical groups",
                    "Use recommended dosages",
                    "Avoid repeated applications",
                    "Combine with other methods",
                ],
                "economic_considerations": [
                    "Calculate cost-benefit ratio",
                    "Consider treatment thresholds",
                    "Focus on high-value crops",
                    "Plan for long-term sustainability",
                ],
            },
            "diagnostic_guide": {
                "symptom_identification": {
                    "leaf_symptoms": {
                        "spots": "Look for size, shape, color, and pattern",
                        "yellowing": "Check if systemic or localized",
                        "wilting": "Determine if vascular or root-related",
                        "deformation": "Note curling, twisting, or stunting",
                    },
                    "stem_symptoms": {
                        "cankers": "Check for sunken, discolored areas",
                        "galls": "Look for swellings or growths",
                        "rot": "Examine for soft, discolored tissue",
                    },
                    "root_symptoms": {
                        "rot": "Check for brown, mushy roots",
                        "galls": "Look for swellings on roots",
                        "stunting": "Compare with healthy plants",
                    },
                },
                "environmental_factors": [
                    "Recent weather conditions",
                    "Irrigation practices",
                    "Fertilization history",
                    "Previous crop history",
                    "Nearby infected plants",
                ],
                "sampling_guidelines": [
                    "Collect samples from disease margins",
                    "Include both healthy and diseased tissue",
                    "Avoid contaminated samples",
                    "Store samples properly for testing",
                ],
            },
        }

    def get_disease_by_symptoms(
        self, symptoms: List[str], crop: str = None
    ) -> List[Dict[str, Any]]:
        """
        Get possible diseases based on symptoms and crop type.

        Args:
            symptoms: List of observed symptoms
            crop: Crop type (optional)

        Returns:
            List of possible diseases with match scores
        """
        possible_diseases = []

        for disease_id, disease_data in self.disease_data["diseases"].items():
            # Check crop match
            if crop and crop.lower() not in [
                c.lower() for c in disease_data.get("affected_crops", [])
            ]:
                continue

            # Calculate symptom match score
            match_score = 0
            total_symptoms = 0

            for symptom_category in disease_data.get("symptoms", {}).values():
                if isinstance(symptom_category, list):
                    total_symptoms += len(symptom_category)
                    for symptom in symptom_category:
                        for user_symptom in symptoms:
                            if user_symptom.lower() in symptom.lower():
                                match_score += 1

            if match_score > 0:
                confidence = (
                    (match_score / total_symptoms) * 100 if total_symptoms > 0 else 0
                )
                possible_diseases.append(
                    {
                        "disease_id": disease_id,
                        "disease_name": disease_data.get("name", ""),
                        "confidence": round(confidence, 1),
                        "category": disease_data.get("category", ""),
                        "severity": disease_data.get("severity", ""),
                        "matched_symptoms": match_score,
                    }
                )

        # Sort by confidence score
        possible_diseases.sort(key=lambda x: x["confidence"], reverse=True)

        return possible_diseases[:5]  # Return top 5 matches
