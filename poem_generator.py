import streamlit as st
from snowflake.snowpark.context import get_active_session
from snowflake.snowpark.functions import col
# import snowflake.connector

# Get the current credentials
# session = get_active_session()
cnx = st.connection("snowflake")
session = cnx.session()

def display_title():
    st.title(":rose: Valentine's Day Poem Generator :rose:")
    st.write(":cupid: Generate a personalized poem for your Valentine's Day :cupid:")

def user_input():
    from_name = st.text_input(":hearts: Your name")
    to_name = st.text_input(":hearts: Your valentine's name")
    place = st.text_input(":hearts: Where you two first met (e.g. Restaurant L'Évidence, Cafe Olimpico, University of Ottawa)")
    # To handle names with single quotes
    place = place.replace("'", "\\'") 
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
                
                # Version 1: Simple, but may have SQL injection
                # insert_stmt = f"""insert into valentine_db.support_data.user_input(user_name,insert_time)
                #               values ('{from_name}',CURRENT_TIMESTAMP)"""
                # session.sql(insert_stmt).collect()
                
                # Version 2: To avoid SQL injection, if using a Snowflake connector (snowflake.connector.connect()) 
                # insert_stmt = f"""insert into valentine_db.support_data.user_input(user_name,insert_time)
                #               values (%s,CURRENT_TIMESTAMP)"""
                # cursor.execute(insert_stmt, (from_name,))
                
                # Version 3: To avoid SQL injection, if using get_active_session()
                insert_stmt = """insert into valentine_db.support_data.user_input(user_name,insert_time)
                              values (?,CURRENT_TIMESTAMP)"""
                session.sql(insert_stmt, params=[from_name]).collect()

            except:
                st.write('Please ensure your input does not have any special characters in the name fields')
    else:
        st.write('** Please fill all the fields before continuing. Press Enter after filling each field. **')

display_title()
from_name, to_name, place, selected_genre = user_input()
generate_poem(from_name, to_name, place, selected_genre)
