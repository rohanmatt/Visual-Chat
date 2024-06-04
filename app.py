from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings

from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
import os
import pickle
from PIL import Image
from io import BytesIO
from streamlit_option_menu import option_menu
import requests
import pandas as pd
import openai
import streamlit as st
#import streamlit_nested_layout
import r_utils as rohans
import warnings
warnings.filterwarnings("ignore")




over_theme = {'txc_inactive': '#ffffff','menu_background':'#5C31FF'}
primaryColor = '#5C31FF'

st.set_page_config(
    page_title='VisualChat:',
    # page_icon = im,
    layout = 'wide',
    initial_sidebar_state = 'auto'
)


with st.sidebar:
        selected = option_menu(
            menu_title = "Main Menu",
            options = ["About the App","Charts",])

if selected == "Charts":
# List to hold datasets
    if "datasets" not in st.session_state:
        datasets = {}
        
        st.session_state["datasets"] = datasets
    else:
        # use the list already loaded
        datasets = st.session_state["datasets"]

    my_key = ""
    uploaded_file = st.file_uploader(" Load a CSV file:", type="csv")

    with st.sidebar:
        # First we want to choose the dataset, but we will fill it with choices once we've loaded one
        dataset_container = st.empty()

        # Add facility to upload a dataset
        # uploaded_file = st.file_uploader(" Load a CSV file:", type="csv")
        index_no=0
        if uploaded_file is not None:
            # Read in the data, add it to the list of available datasets
            file_name = uploaded_file.name[:-4].capitalize()
            datasets[file_name] = pd.read_csv(uploaded_file)
            # Default for the radio buttons
            index_no = len(datasets)-1

        # Radio buttons for dataset choice
        chosen_dataset = dataset_container.radio("Choose your data:",datasets.keys(),index=index_no)#,horizontal=True,)

        # Check boxes for model choice
        # Keep a dictionary of whether models are selected or not
        available_models = {"ChatGPT-3.5": "gpt-3.5-turbo",}
        use_model = {'ChatGPT-3.5': True}
    
    

    # Text area for query
    question = st.text_area("What would you like to visualise?",height=10)
    go_btn = st.button("Generate ")

    # Make a list of the models which have been selected
    #model_dict = {model_name: use_model for model_name, use_model in use_model.items() if use_model}
    #model_count = len(model_dict)
    model_list = [model_name for model_name, choose_model in use_model.items() if choose_model]
    # print("Model list =  ",model_list)
    model_count = len(model_list)

    # Execute chatbot query
    if go_btn and model_count > 0:
        # Place for plots depending on how many models
        plots = st.columns(model_count)
        # Get the primer for this dataset
        primer1,primer2 = rohans.get_primer(datasets[chosen_dataset],'datasets["'+ chosen_dataset + '"]')
        # Format the question
        question_to_ask = rohans.format_question(primer1,primer2 , question)    
        # Create model, run the request and print the results
        for plot_num, model_type in enumerate(model_list):
            with plots[plot_num]:
                st.subheader("Analysis")
                try:
                    # Run the question
                    answer=""
                    answer = rohans.run_request(question_to_ask, available_models[model_type], key=my_key)
                    # the answer is the completed Python script , should i display the code and give an option to download the code
                    answer = primer2 + answer
                    print(answer)
                    
                    # lol = st.text_area(answer,pol)
            
                    plot_area = st.empty()
                    plot_area.pyplot(exec(answer)) 
                    pol =  rohans.ques(answer, available_models[model_type], key=my_key)
                    print("done")
                    
                #     plot_download_button = st.download_button(
                #     label="Download Plot",
                #     data=plot_area,
                #     key="plot_download_button",
                #     file_name="plot.png",
                # )
                    content_column, answer_column = st.columns(2)
                    with content_column:
                        st.write("Python Code:")
                        st.text(answer)
                        content_download_button = st.download_button(
                            label="Download Code",
                            data=answer,
                            key="content_download_button",
                            file_name="content.txt",
                        )
                    with answer_column:
                        st.write("Code Explaination:")
                        st.text(pol)
                        variable_download_button = st.download_button(
                            label="Download Explaination",
                            data=pol,
                            key="variable_download_button",
                            file_name="answer.txt",
                        )
                    
                    
                    
          
                except Exception as e:
                    if type(e) == openai.error.APIError:
                        st.error("OpenAI API Error. Please try again a short time later.")
                    elif type(e) == openai.error.Timeout:
                        st.error("OpenAI API Error. Your request timed out. Please try again a short time later.")
                    elif type(e) == openai.error.RateLimitError:
                        st.error("OpenAI API Error. You have exceeded your assigned rate limit.")
                    elif type(e) == openai.error.APIConnectionError:
                        st.error("OpenAI API Error. Error connecting to services. Please check your network/proxy/firewall settings.")
                    elif type(e) == openai.error.InvalidRequestError:
                        st.error("OpenAI API Error. Your request was malformed or missing required parameters.")
                    elif type(e) == openai.error.AuthenticationError:
                        st.error("Please enter a valid OpenAI API Key.")
                    elif type(e) == openai.error.ServiceUnavailableError:
                        st.error("OpenAI Service is currently unavailable. Please try again a short time later.")                   
                    else:
                        st.error("Unfortunately the code generated from the model contained errors and was unable to execute. ")
       
    # Display the datasets in a list of tabs
    # Create the tabs
    tab_list = st.tabs(datasets.keys())

    # Load up each tab with a dataset
    for dataset_num, tab in enumerate(tab_list):
        with tab:
            # Couldnt get the name of the tab and index key,  So converted to list and index
            dataset_name = list(datasets.keys())[dataset_num]
            st.subheader(dataset_name)
            st.dataframe(datasets[dataset_name])


                
            
                
        

            
        # Hide menu and footer
        hide_streamlit_style = """
                    <style>
                    #MainMenu {visibility: hidden;}
                    footer {visibility: hidden;}
                    </style>
                    """
        st.markdown(hide_streamlit_style, unsafe_allow_html=True)

if selected == "About the App":
    st.markdown("""
                ## 📊 VisualChat: Intelligent Charts and Conversations!
                
                #### Welcome to VisualChat, your go-to app for generating insightful charts from CSV files while seamlessly interacting with your data. Here's what makes us stand out:

                ##### ✅ Our app is organized to do the following financial functions for you 

                ###### Visualize Insights:
                You can visualize and create charts according to your desire for multiple files. 

                ##### ⭐️ Seamless CSV Integration: Harness the power of your data effortlessly. VisualChat seamlessly integrates with CSV files, transforming raw data into actionable insights. No more data struggles our app streamlines the process for you.
                ##### 🛫 Instant Insights: Access valuable insights in an instant. With VisualChat, you'll receive real-time visualizations that highlight key trends and patterns. Transform complex data into actionable insights with just a few clicks.
                ##### 📊 Optimize Decision-Making: Empower your decisions with data-driven insights. VisualChat helps you optimize resource allocation, plan strategies, and stay ahead of the curve. Make informed choices that drive success.
                ##### 🚀 Efficient Operations: Enhance efficiency with VisualChat. By automating data visualization and analysis, you save valuable time and resources. Spend less time crunching numbers and more time focusing on strategic planning.
                

        """)