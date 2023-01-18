---
author: Vedat Baday
title: Notes on Full Stack Deep Learning
date: 2022-01-19
description: My notes on Full Stack Deep Learning course
tags: ["deep-learning", "mlops"]
summary: " "
---


### Lecture 1: Course Vision and When to Use ML
* We avoid an AI winter by translating research progress to real-world products
* “Flat-earth” ML:Classical machine learning workflow in research
   * In production, complexity of monitoring and deploying is also exists
* FSDL is not an MLOps course but it aims to teach enough MLOps to get things done
* **You do not need perfect infrastructure nor the perfect model to start**
* You should not aim for 100% success in ML projects
* A team that is great at developing a model might not be the right team to deploy that model to production
* Machine Learning introduces a lot of complexity
   * ***Optional Reading***: “Machine Learning: The High-Interest Credit Card of Technical Debt”
* Look for “high impact, low cost” problems first
   * low cost projects are that data is available and bad predictions are not too harmful
* Assessing feasibility of ML Projects
   * Data availability
      * Collecting data, cost of labeling, volume of the needed data, security requirements of the data
   * Accuracy requirement
      * Cost of the wrong predictions
      * Ethical implications of the predictions
   * Problem difficulty
      * Definition of the problem
      * Research on the problem (academia)
      * Compute requirements
* Keep track of state-of-the-art solutions to be able to comment on whether a problem is feasible or not
* Machine learning product archetypes
   * ***Software 2.0:*** Taking something software does today and doing it better with ML
   * ***Human-in-the-loop:*** Helping human do their jobs better by supporting them with ML-based tools
   * ***Autonomous systems:*** Taking something done by humans and automating it with ML