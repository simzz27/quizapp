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
    request.session.flush()
    player_name = None  # Initialize player_name as None
    player_image = None  # Initialize player_image as None

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

    # Handle player name selection from the POST request
    if request.method == 'POST' and 'player_name' in request.POST:
        # Set the selected player name in the session
        player_name = request.POST.get('player_name')
        request.session['player_name'] = player_name
        return redirect('quiz:quiz_page', session_id=session.id)  # Redirect to refresh the page

    # Fetch the player name from session
    player_name = request.session.get('player_name', 'Player')  # Default to 'Player' if not set
    print(player_name)
    player_image = names_and_images.get(player_name)

    # Fetch the list of questions that have not been asked yet
    # Get the list of previously asked questions from the session, or initialize it as an empty list
    asked_questions = request.session.get('asked_questions', [])

    # Retrieve questions not yet asked
    remaining_questions = Question.objects.exclude(id__in=asked_questions)

    # If no remaining questions, redirect to results page
    if not remaining_questions.exists():  # Use `.exists()` for efficient checking
        return redirect('quiz:quiz_result', session_id=session.id)

    # Select a random question from the remaining questions
    question = random.choice(list(remaining_questions))  # Convert queryset to list for random.choice

    # Add the question's ID to the session's asked questions list
    asked_questions.append(question.id)
    request.session['asked_questions'] = asked_questions

    # Save the session explicitly
    request.session.modified = True  # Mark the session as modified to ensure it is saved

    message = None  # Initialize the message variable

    if request.method == 'POST' and 'answer' in request.POST:
        # Get the user's answer
        user_answer = int(request.POST.get('answer'))
        answer = question.correct_option
        
        if user_answer == answer:
            session.incorrect_answers += 1
            message = "Correct!"
        else:
            session.correct_answers += 1
            message = "Incorrect."

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
        "player_image": player_image
    })

# Result page view
def quiz_result(request, session_id):
    session = QuizSession.objects.get(id=session_id)

    # Determine the message based on the number of correct answers
    if session.correct_answers == session.total_questions:
        message = "Great Job!"
    elif session.correct_answers == session.total_questions - 1:
        message = "Awesome!"
    else:
        message = "Better Luck Next Time!"


    if not session:
        return redirect('quiz:start_quiz')  # Redirect if session is missing

    return render(request, 'quiz/quiz_result.html', {'session': session, 'message': message})
