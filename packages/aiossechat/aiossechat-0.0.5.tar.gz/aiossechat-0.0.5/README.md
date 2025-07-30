
build cmd：
 ```python setup.py sdist bdist_wheel```

upload cmd:
 ```twine upload dist/*```

If fail：
 - 不要用powershell，可能複製token錯誤，用cmd
 - 大概率是"file exist", 因為忘了改版本號
