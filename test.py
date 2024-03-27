
from src.controller import *

controller = CONTROLLER('bolt://localhost:7687','neo4j','neo4j','/data1/xzk/Allspark/easyedit/hparams/grace/llama-7B.yaml')
controller.kg.clear()

triple1 = ("Joe_Biden","party","Democratic_Party")
controller.edit_knowledge(triple1)

triple2 = ("Joe_Biden","president","United_States")
controller.edit_knowledge(triple2)

triple3 = ("Democratic_Party","country","United_States")
controller.edit_knowledge(triple3)

triple4 = ("Democratic_Party","headquarters","Washington,_D.C.")
controller.edit_knowledge(triple4)
