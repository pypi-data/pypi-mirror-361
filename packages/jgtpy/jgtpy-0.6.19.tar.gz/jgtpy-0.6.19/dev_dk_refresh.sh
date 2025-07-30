pip install -U --index-url https://test.pypi.org/simple/ jgtfxcon &>/dev/null;pip freeze|grep jgtfxcon
pip install -U --index-url https://test.pypi.org/simple/ jgtutils &>/dev/null;pip freeze|grep jgtutils
pip install -U --index-url https://test.pypi.org/simple/ jgtpy &>/dev/null;pip freeze|grep jgtpy


if [ -d /app/dist ];then
 echo " "
  #pip uninstall jgtpy -y &>/dev/null
  #pip install /app/dist/jgtpy-*.whl
fi

#python jgtpy/cdscli.py -i SPX500 -t D1 ;head -n 1 /var/lib/jgt/data/cds/SPX500_D1.csv
