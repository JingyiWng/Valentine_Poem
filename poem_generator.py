import streamlit as st
from snowflake.snowpark.context import get_active_session
from snowflake.snowpark.functions import col
# import snowflake.connector
from htbuilder import HtmlElement, div, ul, li, br, hr, a, p, img, styles, classes, fonts
from htbuilder.units import percent, px
from htbuilder.funcs import rgba, rgb

# Get the current credentials
# session = get_active_session()
# cursor = conn.cursor()
cnx = st.connection("snowflake")
session = cnx.session()

def display_layout():
    # st.title(":rose: Your Personalized Valentine's Day Poem :rose:")
    # st.write(":cupid: Generate a personalized poem for your Valentine's Day :cupid:")
    st.markdown("<h1 style='text-align: center; font-size: 30px; color: #ff4d6d;'>🌹 Your Personalized Valentine's Day Poem 🌹</h1>", unsafe_allow_html=True)
    st.markdown("<h4 style='text-align: center; font-size: 16px; color: #c9184a;'>💘 Generate a personalized poem for your Valentine's Day in seconds 💘</h4>", unsafe_allow_html=True)
    footer()

def user_input():
    display_layout()
    from_name = st.text_input(":hearts: Your name")
    to_name = st.text_input(":hearts: Your valentine's name")
    place = st.text_input(":hearts: Where you two first met (e.g. Restaurant L'Évidence, Cafe Olimpico, University of Ottawa)")
    # To handle names with single quotes
    place = place.replace("'", "\\'") 
    
    # Fetch the poem_genre table from Snowflake backend. Use the genre column as input selection
    all_genres = session.table("valentine_db.support_data.poem_genre").select(col('GENRE'))
    selected_genre = st.selectbox(":hearts: The genre of the poem", all_genres)
    
    return from_name, to_name, place, selected_genre


def generate_poem(from_name, to_name, place, selected_genre):

    prompt = f"""Create a short romantic and personalized poem. The poem is from {from_name} to {to_name}. \
             The place where the two people first met is {place}. \
             Use the information mentioned to create a short poem in less than 200 words in the style of {selected_genre}. \
             Do not include any potentially inappropriate or unsafe language.\
             Do not include any comments/notes in the generated text."""
    cortex_prompt = "\'[INST] " + prompt + " [/INST]\'"
    
    if from_name and to_name and place and selected_genre:
        submit = st.button('Generate My Personalized Poem')
        if submit:
            try:
                # Create a placeholder for the "generating" message
                placeholder = st.empty()
                placeholder.text("Generating...")
             
                cortex_response = session.sql(f"select snowflake.cortex.complete('llama3.1-70b', {cortex_prompt}) as response")\
                                  .to_pandas().iloc[0]['RESPONSE']
                st.write(cortex_response)
             
                # Replace the placeholder content with the result
                placeholder.text("")  # Clear the "generating" message
     
                # Track how many users have used the service
                
                # Version 1: Simple, but may have SQL injection issues
                # insert_stmt = f"""insert into valentine_db.support_data.user_input(user_name,insert_time)
                #               values ('{from_name}',CURRENT_TIMESTAMP)"""
                # session.sql(insert_stmt).collect()
                
                # Version 2: To avoid SQL injection 
                # insert_stmt = f"""insert into valentine_db.support_data.user_input(user_name,insert_time)
                #               values (%s,CURRENT_TIMESTAMP)"""
                # cursor.execute(insert_stmt, (from_name,))
                
                # Version 3: To avoid SQL injection
                insert_stmt = """insert into valentine_db.support_data.user_input(user_name,insert_time)
                              values (?,CURRENT_TIMESTAMP)"""
                session.sql(insert_stmt, params=[from_name]).collect()

            except:
                st.write('Please ensure your input does not have any special characters in the name fields')
    else:
        st.write('** Please fill all the fields before continuing. Press Enter after filling each field. **')
        

# Create the footer section
def image(src_as_string, **style):
    return img(src=src_as_string, style=styles(**style))

def link(link, text, **style):
    return a(_href=link, _target="_blank", style=styles(**style))(text)

def layout(*args):

    style = """
    <style>
      # MainMenu {visibility: hidden;}
      footer {visibility: hidden;}
     .stApp { bottom: 105px; }
    </style>
    """

    style_div = styles(
        position="fixed",
        left=0,
        bottom=0,
        margin=px(0, 0, 0, 0),
        width=percent(100),
        color="black",
        text_align="center",
        height="auto",
        opacity=1
    )

    style_hr = styles(
        display="block",
        margin=px(8, 8, "auto", "auto"),
        border_style="inset",
        border_width=px(2)
    )

    body = p()
    foot = div(
        style=style_div
    )(
        hr(
            style=style_hr
        ),
        body
    )

    st.markdown(style, unsafe_allow_html=True)

    for arg in args:
        if isinstance(arg, str):
            body(arg)

        elif isinstance(arg, HtmlElement):
            body(arg)

    st.markdown(str(foot), unsafe_allow_html=True)

def footer():
    myargs = [
        "Made in ",
        image('https://media.graphcms.com/s1HsxaRlS7tzWLmgMwq9',
              width=px(25), height=px(25)),
        " with ❤️ by ",
        link("https://www.linkedin.com/in/jenn-jw/", "@Jenn_Wang"),
        br(),
    ]
    layout(*myargs)




# Get the input provided by user
from_name, to_name, place, selected_genre = user_input()
generate_poem(from_name, to_name, place, selected_genre)





