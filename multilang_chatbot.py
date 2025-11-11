from dotenv import load_dotenv
import os
#Import namespaces for chatbot service 
from azure.core.credentials import AzureKeyCredential
from azure.ai.language.questionanswering import QuestionAnsweringClient
from azure.ai.translation.text.models import InputTextItem
from azure.ai.translation.text import TranslatorCredential, TextTranslationClient

"""
The Python file integrates the following:  
#Question: Section B, Part A, No. 5 (used for English chatbot)  
#Question: Section B, Part B, No. 4 (used for multilanguage chatbot)  
Start Run 
1. Right click multilang_chatbot.py click "Open Integreated Terminal"
2. Enter text : "python multilang_chatbot.py"
3. Input text questions english or chinese or japan. 
   chatbot will reply answer your input language.
4.Enter "quit" to exit program.
"""
def main():
    try:
        # Load environment variables
        load_dotenv()
        
        # Chatbot configuration
        ai_endpoint = os.getenv('AI_SERVICE_ENDPOINT')
        ai_key = os.getenv('AI_SERVICE_KEY')
        ai_project_name = os.getenv('QA_PROJECT_NAME')
        ai_deployment_name = os.getenv('QA_DEPLOYMENT_NAME')

        # Translator configuration
        translator_region = os.getenv('TRANSLATOR_REGION')
        translator_key = os.getenv('TRANSLATOR_KEY')

        # Initialize clients
        ai_credential = AzureKeyCredential(ai_key)
        ai_client = QuestionAnsweringClient(endpoint=ai_endpoint, credential=ai_credential)

        translator_credential = TranslatorCredential(translator_key, translator_region)
        translator_client = TextTranslationClient(translator_credential)

        # Supported language check for translation
        languages_response = translator_client.get_languages(scope="translation")
        #supported_languages = languages_response.translation.keys()

        print("If you want quit from chatbot. Please type your questions (type 'quit' to exit):")

        user_question = ''
        while user_question.lower() != 'quit':
            user_question = input('\nQuestion : ')
            if user_question.lower() == 'quit':
                break
            
            # Detect if the input is in English or another language
            input_text_elements = [InputTextItem(text=user_question)]
            translation_response = translator_client.translate(content=input_text_elements, to=['en'])
            detected_language = translation_response[0].detected_language.language
            # Get the detected language code
            question_lang_code = translation_response[0].detected_language.language

            # If the detected language is not English, translate the question
            if detected_language != 'en':
                #Translating to English
                #print(f"Detected language: {detected_language} Question language code {question_lang_code}.")
                user_question = translation_response[0].translations[0].text
                #print(f"Translated question: {user_question}")

            # Submit the translated (or original English) question to the chatbot
            response = ai_client.get_answers(
                question=user_question,
                project_name=ai_project_name,
                deployment_name=ai_deployment_name
            )

            # Display chatbot responses
            if response.answers:
                #print(f"Question language: {detected_language}")
                for candidate in response.answers:
            
                    # Prepare the answer for translation
                    answer_text_elements = [InputTextItem(text=candidate.answer)]
                    translation_ans = translator_client.translate(content=answer_text_elements, to=[question_lang_code])
                    translated_answer = translation_ans[0].translations[0].text
                   
                    #English Answer
                    #Translated Answer by detect input language
                    print(f"Answer : {translated_answer}")

                    #print(f"Confidence: {candidate.confidence}")
                    #if candidate.source:
                        #print(f"Source: {candidate.source}")
            else:
                print(f"Question language: {detected_language}")
                print("No suitable answer found.")

    except Exception as ex:
        print(f"An error occurred: {ex}")

if __name__ == "__main__":
    main()
