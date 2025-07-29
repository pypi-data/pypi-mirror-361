# Trilla Library

Библиотека общих компонентов Trilla 


## pypi сервер
http://10.0.24.204:8080


```shell
poetry config repositories.dev-pypi http://10.0.24.204:8080    
```

```shell
poetry config --unset repositories.dev-pypi
```

```shell
poetry config --list
```

```shell
poetry publish --repository dev-pypi --build
```
```shell
poetry publish
```