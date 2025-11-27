from dotenv import load_dotenv
import os
#Import namespaces for chatbot service 
from azure.core.credentials import AzureKeyCredential
from azure.ai.language.questionanswering import QuestionAnsweringClient
from azure.ai.translation.text.models import InputTextItem
from azure.ai.translation.text import TranslatorCredential, TextTranslationClient

#Import namespaces for Speech service 
import azure.cognitiveservices.speech as speech_sdk

"""
.......................................
Noted: Reference : To get Audio file convert from text to voice file : https://voicemaker.in

"""
def main():
   
    try:
        global input_type
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

        #Supported language check for translation
        #languages_response = translator_client.get_languages(scope="translation")
        #supported_languages = languages_response.translation.keys()
        # set speech service
        speech_service()
       
        user_question = ''
        while True:
            print("Enter 'speech' to play the song or speech for speech input, 'text' to type your question, or 'quit' to exit:")
            user_choice = input("Enter your choice (speech/text/quit): ").lower()
            input_type=user_choice
            # Check if the user wants to quit
            if user_choice == 'quit': #stop running app
                break
            
            # this part is for Section B, Part B, No.5: (i) To incorporate speech-to-text in the code.
            if user_choice == 'speech':  # Speech input via playing a song
                 # Get spoken input
                speech_input_text = TranscribeCommand()
                if speech_input_text.strip():  # If speech input is available
                    user_question = speech_input_text
                else:
                    print("No speech input detected. Please try again.")
                    continue

            elif user_choice == 'text':  # Manual text input
                text_question = input('\nQuestion(type question):')
                if text_question.strip():  # If the user typed something
                    user_question = text_question
                else:
                    print("No text input provided. Please try again.")
                    continue

            else:
                print("Invalid choice. Please type 'speech' or 'text'.")
                continue

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
                    print(f"Answer: {translated_answer}")
                    
                    #this part is for Section B, Part B, No.5: (i) To incorporate speech-to-text in the code.
                    if user_choice=="speech":#if user was asked question by speech.
                         #print("Please wait while processing convert speech to text...")
                         TextToSpeech(translated_answer)

                    #print(f"Confidence: {candidate.confidence}")
                    #if candidate.source:
                        #print(f"Source: {candidate.source}")
            else:
                print(f"Question language: {detected_language}")
                print("No suitable answer found.")

    except Exception as ex:
        print(f"An error occurred: {ex}")


#setup configuration speech service 
def speech_service():
    try:
        global speech_config
    
        ai_key = os.getenv('SPEECH_KEY')
        ai_region = os.getenv('SPEECH_REGION')

        # Configure speech service
        speech_config = speech_sdk.SpeechConfig(ai_key, ai_region)
        print('Ready to use speech service in:', speech_config.region)       
    

    except Exception as ex:
        print(ex)

#this part is for Section B, Part B, No.5: (i) To incorporate speech-to-text in the code.
#song voice/speech to text method
def TranscribeCommand():
    command = ''

    #base_path = "/Users/teamone/Documents/assignment/109-FullQuestionProject/Python/multilanguage-chatbot"
    base_path = os.getcwd() #current dir
    audioFile = os.path.join(base_path, "eng_q1.wav")
    #playsound(audioFile)
    #audio_config = speech_sdk.AudioConfig(filename=audioFile)
    audio_config = speech_sdk.AudioConfig(use_default_microphone=True)
    speech_recognizer = speech_sdk.SpeechRecognizer(speech_config, audio_config)
    print('Speak now...')
    # Process speech input
    speech = speech_recognizer.recognize_once_async().get()
    if speech.reason == speech_sdk.ResultReason.RecognizedSpeech:
        command = speech.text
        print(f"Question: {command}")
    else:
        print(speech.reason)
        if speech.reason == speech_sdk.ResultReason.Canceled:
            cancellation = speech.cancellation_details
            print(cancellation.reason)
            print(cancellation.error_details)

    # Return the command
    return command

#this part is for Section B, Part B, No.5: (ii) To incorporate text-to-speed in the code.
#Text to speech/voice
def TextToSpeech(response_text):
    # Configure speech synthesis
    speech_config.speech_synthesis_voice_name = "en-GB-RyanNeural"
    speech_synthesizer = speech_sdk.SpeechSynthesizer(speech_config)

    # Synthesize spoken output
    speak = speech_synthesizer.speak_text_async(response_text).get()
    if speak.reason != speech_sdk.ResultReason.SynthesizingAudioCompleted:
        print(speak.reason)

    #Print the response
    #print(f"Answer: {response_text}")

if __name__ == "__main__":
    main()
