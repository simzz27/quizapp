import random
from django.shortcuts import render, redirect
from .models import Question, QuizSession

# Dictionary for player names and images
names_and_images = {
    "Lily": 'images/player1.png',
    "Mia": 'images/player2.png',
    "Leo": 'images/player3.png',
    "Max": 'images/player4.png'
}

# Home view to select the player
def home(request):
    player_name = None  # Initialize player_name as None
    player_image = None  # Initialize player_image as None
    print("Form submitted!")

    if request.method == 'POST':
        # Get the selected player name and image from the form
        player_name = request.POST.get('player_name')
        player_image = names_and_images.get(player_name)
        

        if player_name:
            # Store player data in the session
            request.session['player_name'] = player_name
            request.session['player_image'] = player_image

            # Create a session object in the QuizSession model
            session = QuizSession.objects.create(player_name=player_name)

            # Initialize the asked_questions list in the session
            request.session['asked_questions'] = []

            return redirect('quiz:start_quiz')  # Redirect to the start quiz page
    
    # If no POST, pick a random player
    # if not player_name:
    #     player_name = random.choice(list(names_and_images.keys()))  # Assign a random player name
    #     player_image = names_and_images.get(player_name)

    # Store random player data in the session if no player was selected
    request.session['player_name'] = player_name
    request.session['player_image'] = player_image

    session = QuizSession.objects.create(player_name=player_name)

    return render(request, 'quiz/quiz_home.html', {'session': session, 'player_name': player_name, 'player_image': player_image})

def start_quiz(request):
    # Check if a player is selected or if a player data is passed in the session
    player_name = request.session.get('player_name', None)
    
    if player_name:
        # Redirect the player to the quiz page with their selected name
        return render(request, 'quiz/start_quiz.html', {'player_name': player_name})
    else:
        # If no player is selected, you can redirect them to a selection page
        return redirect('select_player')  # Adjust the name of your player selection page


# Quiz page view
def quiz_page(request, session_id):
    session = QuizSession.objects.get(id=session_id)
    
    # Fetch the player name and image from session
    player_name = request.session.get('player_name')
    player_image = request.session.get('player_image')

    if not player_name or not player_image:
        return redirect('quiz:home')  # If no player data found, redirect to home

    # Fetch the list of questions that have not been asked yet
    asked_questions = request.session.get('asked_questions', [])
    remaining_questions = Question.objects.exclude(id__in=asked_questions)

    if not remaining_questions:
        return redirect('quiz:quiz_result', session_id=session.id)  # All questions are answered

    question = random.choice(remaining_questions)

    # Add this question to the list of asked questions
    asked_questions.append(question.id)
    request.session['asked_questions'] = asked_questions

    message = None  # Initialize the message variable

    if request.method == 'POST':
        # Get the user's answer
        user_answer = int(request.POST.get('answer'))
        correct_answer = question.correct_option
        
        if user_answer == correct_answer:
            session.correct_answers += 1
            message = "Correct!"
        else:
            session.incorrect_answers += 1
            message = f"Incorrect. The correct answer is option {correct_answer}."

        # Increment total question count and save the session
        session.total_questions += 1
        session.save()

        # If all questions are answered, show the results
        QUESTION_LIMIT = 5
        if session.total_questions >= QUESTION_LIMIT:
            return redirect('quiz:quiz_result', session_id=session.id)

        # Redirect to next question
        return redirect('quiz:quiz_page', session_id=session.id)

    return render(request, 'quiz/quiz_page.html', {
        'session': session, 
        'question': question, 
        'message': message, 
        'player_name': player_name,
        'player_image': player_image,  # Player image is fetched from session
    })


# Result page view
def quiz_result(request, session_id):
    session = QuizSession.objects.get(id=session_id)

    if not session:
        return redirect('quiz:start_quiz')  # Redirect if session is missing

    return render(request, 'quiz/quiz_result.html', {'session': session})
