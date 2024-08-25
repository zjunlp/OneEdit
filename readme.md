<h1 align="center"> OneEdit </h1>
<h3 align="center"> OneEdit: A Neural-Symbolic Collaboratively Knowledge Editing System </h3>

<p align="center">
  <img src="overview.png" alt="示例图片">
</p>

<center>
  ![示例图片](overview.png)
</center>

[![Awesome](https://awesome.re/badge.svg)](https://github.com/zjunlp/KnowledgeCircuits) 
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
![](https://img.shields.io/github/last-commit/zjunlp/KnowledgeCircuits?color=green) 


Quick Start
## Table of Contents
- 🌟[Overview](#overview)
- 🔧[Installation](#installation)
- 📚[Quick Start](#Quick-Start)
- 🧐[Demo](#demo)

---

## 🌟Overview

Since the inception of artificial intelligence, knowledge representation has always been one of its core objectives. This work primarily focuses on integrating the parametric knowledge of large language models with symbolic knowledge, enabling more precise modifications to the model's parametric knowledge.


## 🔧Installation
### Conda Environment
Build the environement:
```
conda create -n oneedit python=3.10
pip install -r requirements.txt
```
### Neo4j
You need to download and install [Neo4j](https://neo4j.com/download-center/#community) locally, and ensure that your computer has the necessary permissions to access Neo4j.
We used neo4j-enterprise-3.5.35 in our experiments.

## 📚Quick Start
### Start neo4j
First, you need to start the Neo4j service and ensure that the local ports 7474 and 7687 are available.
```
neoj4 start
```
### Set Editor Hparam
You need to set the name of the model you want to run and the knowledge editing method in the edit_method and model_name fields of the hparam file. Currently, we only support GRACE and MEMIT, with partial support for ROME.
### Set Noo4j Hparam
You need to specify your Neo4j URL, username, and password in the hyperparameters.
### Set Interpreter Hparam
Finally, you need to specify the path for the interpreter. We provide a LoRA-trained MiniCPM 2B model for you to use. You can download it and then set the path accordingly.

Then, you can load the data according to the path specified in the project and run the code by entering the following command.
```
python exp.py \
  --datapath data_path \
  --harampath haram_path
```

## 🧐Demo
We provide a user-friendly web interface to facilitate ease of use.

First, you need to start our service on the backend.
```
python server.py
```
Then, you can run the web code to test the model outputs and observe changes in the knowledge graph in real time.
```
cd web
yarn dev start
```