**Seetup and run :**

---

  
packages to install:  
 - numpy  
 - matplotlib  
 - jupyterlab  
 - notebook  
 - voila


*install with the : pip install <name>*

---

*Running the actual file / scrypt :*

 - jupyter lab <- for main config and stuff  (currently wrote this markdown in it)
 - jupyter notebook <- for opening projects and nice editing  
 - voila <- only for running (without seeing the code)



---

*extra*

 - using this single line of batch you can convert the "jupython" to straight html  
   `jupyter nbconvert --to html <file_name>.ipynb `  
   Limitations : The resulting HTML file is static and does not include interactivity or the ability to run code. It’s more like a snapshot of the notebook.  

 - to be able to run the code in the browser you have to do a lot more :  
   Download the pre-built JupyterLite bundle [from github](https://github.com/jupyterlite/jupyterlite/releases)  
   Place Your .ipynb Files in the JupyterLite Directory  
   Host JupyterLite on Your Web Server  (the entire ducking thing is over 3Mb)
   and i guess just read the "Readme" file 'cus i was lazy to set it up correctly

