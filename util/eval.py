import argparse,json
from sklearn.metrics import confusion_matrix
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import numpy as np

# Existe interseccion entre las dos entidades
def interseccion_entidades(ent1,ent2):
    al=ent1['start']
    ar=ent1['end']
    bl=ent2['start']
    br=ent2['end']
    res=bl<=al and al<br    # bl al br 
    res|=bl<=ar and ar<br   # bl ar br
    res|=al<=bl and bl<ar   # al bl ar
    res|=al<=br and br<ar   # al br ar
    return res
# Hay una entidad aprox
def esta_entidad(ent,arr):
    for a in arr:
        if interseccion_entidades(ent,a):
            return True
    return False
# Existe la entidad con aprox
def existe_entidad(ent,arr):
    for a in arr:
        if interseccion_entidades(ent,a) and ent['type']==a['type']:
            return True
    return False
# Comparar las entidades de dos relaciones
def comparar_relaciones(a_head,a_tail,b_head,b_tail):
    res=interseccion_entidades(a_head,b_head) and interseccion_entidades(a_tail,b_tail)    
    res|=interseccion_entidades(a_head,b_tail) and interseccion_entidades(a_tail,b_head)
    return res

# Calcular las relaciones en dos arrays
def calculo_rels():
    print('> Realizando el calculo para la cm de relaciones')

    y_true=[]
    y_pred=[]
    for pred,y in zip(info_pred,info_y):
        ents_p=pred['entities']
        rels_p=[x for x in pred['relations']]
        ents_gold=y['entities']
        rels_gold=[x for x in y['relations']]
        # Mismo type
        for rg in y['relations']:
            head_rg=ents_gold[rg['head']]
            tail_rg=ents_gold[rg['tail']]
            for rp in rels_p:
                head_rp=ents_p[rp['head']]
                tail_rp=ents_p[rp['tail']]
                if rg['type']==rp['type'] and comparar_relaciones(head_rg,tail_rg,head_rp,tail_rp):
                    rels_p.remove(rp)
                    rels_gold.remove(rg)
                    y_true.append(rg['type'])
                    y_pred.append(rp['type'])
                    break   
        # Distinto type 
        aux=[x for x in rels_gold] 
        for rg in aux:
            head_rg=ents_gold[rg['head']]
            tail_rg=ents_gold[rg['tail']]
            for rp in rels_p:
                head_rp=ents_p[rp['head']]
                tail_rp=ents_p[rp['tail']]
                if comparar_relaciones(head_rg,tail_rg,head_rp,tail_rp):
                    rels_p.remove(rp)
                    rels_gold.remove(rg)
                    y_true.append(rg['type'])
                    y_pred.append(rp['type'])
                    break  
        # Restantes gold   
        for rg in rels_gold:
            head_rg=ents_gold[rg['head']]
            tail_rg=ents_gold[rg['tail']]
            if existe_entidad(head_rg,ents_p) and existe_entidad(tail_rg,ents_p):
                y_true.append(rg['type'])
                y_pred.append('null') # No se ha detectado la relacion
            else:
                y_true.append(rg['type'])
                y_pred.append('incompleta') # Falta alguna entidad
        # Restantes pred   
        for rp in rels_p:
            head_rp=ents_p[rp['head']]
            tail_rp=ents_p[rp['tail']]
            if existe_entidad(head_rp,ents_gold) and existe_entidad(tail_rp,ents_gold):
                y_pred.append(rp['type'])
                y_true.append('null') # No se ha detectado la relacion
            else:
                y_pred.append(rp['type'])
                y_true.append('incompleta') # Falta alguna entidad
    return y_true,y_pred
# Calcular las entidades en dos arrays
def calculo_ent():
    print('> Realizando el calculo para la cm de las entidades aprox')
    
    y_true=[]
    y_pred=[]
    for pred,y in zip(info_pred,info_y):
        ents_p=[x for x in pred['entities']]
        ents_gold=[x for x in y['entities']]
        # Mismo type
        for eg in y['entities']:
            for ep in pred['entities']:
                if eg['type']==ep['type'] and interseccion_entidades(eg,ep):
                    try:
                        ents_p.remove(ep)
                    except:
                        0
                    ents_gold.remove(eg)
                    y_true.append(eg['type'])
                    y_pred.append(ep['type'])
                    break
        # Distinto type
        aux=[x for x in ents_gold]
        for eg in aux:
            for ep in ents_p:
                if interseccion_entidades(eg,ep):
                    ents_p.remove(ep)
                    ents_gold.remove(eg)
                    y_true.append(eg['type'])
                    y_pred.append(ep['type'])
                    break
        # Restantes gold
        for eg in ents_gold:
            y_true.append(eg['type'])
            y_pred.append('null')
        # Restantes pred
        for ep in ents_p:
            y_true.append('null')
            y_pred.append(ep['type'])

    return y_true,y_pred
# Crear la matriz de confusion
def conf_matrix(y_true, y_pred, filename, labels, ymap=None, figsize=(10,7)):
    """
    Generate matrix plot of confusion matrix with pretty annotations.
    The plot image is saved to disk.
    args: 
      y_true:    true label of the data, with shape (nsamples,)
      y_pred:    prediction of the data, with shape (nsamples,)
      filename:  filename of figure file to save
      labels:    string array, name the order of class labels in the confusion matrix.
                 use `clf.classes_` if using scikit-learn models.
                 with shape (nclass,).
      ymap:      dict: any -> string, length == nclass.
                 if not None, map the labels & ys to more understandable strings.
                 Caution: original y_true, y_pred and labels must align.
      figsize:   the size of the figure plotted.
    """
    print('> Generando la confusion matrix')

    if ymap is not None:
        y_pred = [ymap[yi] for yi in y_pred]
        y_true = [ymap[yi] for yi in y_true]
        labels = [ymap[yi] for yi in labels]
    cm = confusion_matrix(y_true, y_pred, labels=labels)
    cm_sum = np.sum(cm, axis=1, keepdims=True)
    cm_perc = cm / cm_sum.astype(float) * 100
    annot = np.empty_like(cm).astype(str)
    nrows, ncols = cm.shape
    for i in range(nrows):
        for j in range(ncols):
            c = cm[i, j]
            p = cm_perc[i, j]
            if i == j:
                s = cm_sum[i]
                annot[i, j] = '%.1f%%\n%d/%d' % (p, c, s)
            elif c == 0:
                annot[i, j] = ''
            else:
                annot[i, j] = '%.1f%%\n%d' % (p, c)
    cm = pd.DataFrame(cm_perc, index=labels, columns=labels) #cm
    cm.index.name = 'Actual'
    cm.columns.name = 'Predicted'
    fig, ax = plt.subplots(figsize=figsize)
    sns.heatmap(cm, annot=annot, fmt='', ax=ax)
    plt.savefig(filename)
    
if __name__=='__main__':
    parser = argparse.ArgumentParser(description='Crea las matrices de confusion de entidades y relaciones.')
    # > predictions_test_epoch_0.json       test.json  
    # < model_mc_ent.png    model_mc_rel.png
    # Los porcentajes de la mc es el recall
    parser.add_argument('model', help='nombre del modelo')
    parser.add_argument('pred_file', help='fichero con las predicciones')
    parser.add_argument('y_file', help='fichero con las respuestas')
    parser.add_argument('-ne', action='store_false',help='no crear la matriz de confusion de entidades',default=True)
    parser.add_argument('-nr', action='store_false',help='no crear la matriz de confusion de relaciones',default=True)
    args = parser.parse_args()

    with open(args.pred_file) as fpred:
        info_pred=json.loads(fpred.read())
    with open(args.y_file) as fy:
        info_y=json.loads(fy.read())

    clases=["diag","pathogen","qol","other","env","biochem","treatment","medC","null"]
    y_true, y_pred=calculo_ent()
    if args.ne:
        conf_matrix(y_true, y_pred, args.model+"_mc_ent.png", clases, ymap=None, figsize=(10,7))

    clases=["diagnoses","influences","causes","other","is_type_of","treats","side_effect_of","has_symptom","is_similar_to","prevents","interaction","treat-medC","null",'incompleta']
    y_true, y_pred=calculo_rels()
    if args.nr:
        conf_matrix(y_true, y_pred, args.model+"_mc_rel.png", clases, ymap=None, figsize=(20,14))
    