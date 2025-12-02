python3 -m venv venv
source venv/bin/activate
pip install streamlit pandas numpy
pip freeze > requirements.txt
mkdir data
streamlit run streamlit_app.py
