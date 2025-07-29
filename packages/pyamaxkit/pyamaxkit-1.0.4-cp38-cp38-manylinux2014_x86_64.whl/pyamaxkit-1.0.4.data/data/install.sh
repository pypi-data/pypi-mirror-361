pushd dist
python3 -m pip uninstall pyamaxkit -y;python3 -m pip install ./pyamaxkit-*.whl
popd
