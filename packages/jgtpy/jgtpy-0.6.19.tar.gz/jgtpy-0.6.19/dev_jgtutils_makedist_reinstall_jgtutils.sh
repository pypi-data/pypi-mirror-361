(cdjgtutils;make dist) && export jgtutils_whl_path=$(realpath ../jgtutils/dist/*whl) && echo "Installing : $jgtutils_whl_path" && \
	pip uninstall jgtutils -y && pip install $jgtutils_whl_path --force-reinstall && (conda activate baseprod && pip install --user -U $jgtutils_whl_path)

