import streamlit as st
from my_component import my_component
# Add some test code to play with the component while it's in development.
# During development, we can run this just as we would any other Streamlit
# app: `$ streamlit run my_component/example.py`
st.subheader("Component with constant args")
# Create a second instance of our component whose `name` arg will vary
# based on a text_input widget.
#
# We use the special "key" argument to assign a fixed identity to this
# component instance. By default, when a component's arguments change,
# it is considered a new instance and will be re-mounted on the frontend
# and lose its current state. In this case, we want to vary the component's
# "name" argument without having it get recreated.

num_clicks = my_component(positions=["ROW2, COL1","ROW2, COL2","ROW2, COL3","ROW3, COL1","ROW3, COL2","ROW3, COL3","ROW4, COL1","ROW4, COL2","ROW4, COL3","ROW5, COL1","ROW5, COL2","ROW5, COL3","ROW6, COL1","ROW6, COL2","ROW6, COL3","ROW7, COL1","ROW7, COL2","ROW7, COL3","ROW1, COL1(Auto Select)","ROW1, COL2(Auto Select)","ROW1, COL3(Auto Select)"], key="foo")
st.write(num_clicks)
