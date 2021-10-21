# Model Regsitry

Model registry currently supports the below framewoks

* Sklearn
* Tensorflow (*In progress*)
* Pytorch    (*In progress*)
* Spacy      (*In progress*)

## Signature 

Model input and output signature can be inferred using signature method from modelregistry

Usage 

```python
>>> data.head(3)
patientid	dateofobservation	systolic	diastolic	hdl	ldl	bmi	age	start	diabetic
0	02314aa6-55ab-e606-7089-e3185adee368	2015-02-18T14:33:45Z	145.0	111.0	66.1	84.5	29.2	31.221918	2015-02-18	1

>>> import modelregistry
>>> signarure = modelregistry.sklearn.get_signature(data.drop(['patientid','diabetic','dateofobservation','start'],axis=1),
                          model.predict_proba(data.drop(['patientid','diabetic','dateofobservation','start'],axis=1)))

>>>signarure
inputs: 
  ['systolic': string, 'diastolic': string, 'hdl': string, 'ldl': string, 'bmi': string, 'age': double]
outputs: 
  [Tensor('float64', (-1, 2))]
```

## Sklearn

Sklearn models can be saved in two ways,
by using log_model method to save from current code or use saved_model to save already saved model

#### log_model
```python

>>> mr = modelregistry.sklearn.ModelRegister()
>>> mr.log_model(
    'Diabetic', # model name
    model, # model
    'DnA', # model owner
    param_grid, # model params , Null by default
    signarure, # model signature , Null by default
    {
        'pandas' : '1.3.0',
        'numpy'  : '1.21.1'
    }, # Python requirements 
    'Sample App for Demo ' # Null by default
)

```

#### saved_model


```python

>>> mr = modelregistry.sklearn.ModelRegister()
>>> mr.saved_model(
    'Diabeticsaved', # model name
    model_path, # model path
    'DnA', # model owner
    param_grid, # model params , Null by default
    signarure, # model signature , Null by default
    {
        'pandas' : '1.3.0',
        'numpy'  : '1.21.1'
    }, # Python requirements 
    'Sample App for Demo ' # Null by default
)

```
