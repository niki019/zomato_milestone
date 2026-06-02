# Project Context: AI-Powered Restaurant Recommendation System (Zomato Use Case)

This document provides context and architectural flow for the AI-Powered Restaurant Recommendation System, as defined in [problemStatement.txt](file:///e:/doc/problemStatement.txt).

## Goal
To build a personalized recommendation service that leverages structured restaurant data and Large Language Models (LLMs) to deliver human-like, custom-tailored dining suggestions.

## Key Components

### 1. Data Ingestion & Preprocessing
* **Dataset**: [ManikaSaini/zomato-restaurant-recommendation](https://huggingface.co/datasets/ManikaSaini/zomato-restaurant-recommendation) on Hugging Face.
* **Fields of Interest**:
  * Name
  * Location
  * Cuisine
  * Cost
  * Rating

### 2. User Preferences
The system takes user criteria to filter the dataset:
* **Location** (e.g., Delhi, Bangalore)
* **Budget Level** (Low, Medium, High)
* **Cuisine Type** (e.g., Italian, Chinese)
* **Minimum Rating**
* **Special Preferences** (e.g., family-friendly, quick service, romantic)

### 3. LLM Integration Layer
* **Filtering**: Subsets the dataset to matching candidate restaurants.
* **Prompt Engineering**: Constructs a prompt containing the candidate list and user preferences.
* **Reasoning**: Guides the LLM to rank options and justify why they fit the user's specific context.

### 4. Recommendation Output
* Generates a ranked list.
* Provides a personalized explanation/reasoning for each recommendation.
* Formats results clearly showing:
  * Restaurant Name
  * Cuisine
  * Rating
  * Estimated Cost
  * AI-generated explanation
