from flask import Flask, render_template, request, redirect, url_for, flash
import os
from project import img_read_helper, img_save_helper, StandardImageProcessing, PremiumImageProcessing, knn_tests
from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
from project import img_read_helper, knn_tests
from dotenv import load_dotenv  # Load environment variables from .env
from config import Config

load_dotenv()
app = Flask(__name__)
app.secret_key = '\xa3\xcf\xd3\x1b\xa2K\xb3\x9fN\xf0\xfe\xf1\xd0\xba\xe7\xd5\x95\x1b\x08\x8b\xe6\x8f\x10'
# For flash messages
app.config.from_object(Config)

UPLOAD_FOLDER = os.path.join(app.root_path, 'static/uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

OPERATION_COSTS = {
    "1": {"name": "Negate Image", "cost": 5},
    "2": {"name": "Grayscale Image", "cost": 6},
    "3": {"name": "Rotate Image 180°", "cost": 10},
    "4": {"name": "Adjust Brightness", "cost": 1},
    "5": {"name": "Blur Image", "cost": 5}
}

def generate_new_filename(original_path, suffix):
    directory, filename = os.path.split(original_path)
    name, extension = os.path.splitext(filename)
    new_filename = f"{name}{suffix}{extension}"
    return os.path.join(directory, new_filename)

@app.route('/')
def index():
    return render_template('index.html')  # Main menu

@app.route('/process', methods=['GET', 'POST'])
def process_image():
    if request.method == 'POST':
        if 'image' not in request.files:
            flash('No file uploaded')
            return render_template('process.html', operations=OPERATION_COSTS)

        file = request.files['image']
        if file.filename == '':
            flash('No selected file')
            return render_template('process.html', operations=OPERATION_COSTS)

        if file:
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)  # Save the uploaded image
            
            # Process the uploaded image
            processor_type = request.form['processor_type']
            processor = PremiumImageProcessing() if processor_type == 'premium' else StandardImageProcessing()
            operation_choices = request.form.getlist('operations')
            processed_image, total_cost = process_image(processor, operation_choices, file_path, 0)

            if processed_image:
                processed_filename = generate_new_filename(file_path, "_processed")
                img_save_helper(processed_filename, processed_image)
                processed_filename = os.path.basename(processed_filename)
                flash(f'Image processing completed. Total cost: ${total_cost}')
                return render_template('process.html', uploaded_image=filename, processed_image=processed_filename, operations=OPERATION_COSTS)

            flash('An error occurred during image processing.')
            return render_template('process.html', operations=OPERATION_COSTS)

    # This handles the GET request and ensures 'operations' is passed when the page loads
    return render_template('process.html', operations=OPERATION_COSTS)




@app.route('/knn', methods=['GET', 'POST'])
def knn_classifier():
    if request.method == 'POST':
        if 'image' not in request.files:
            flash('No file uploaded')
            return redirect(request.url)

        file = request.files['image']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)

        if file:
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)  # Save the file to the upload folder

            # Run the KNN classifier
            predicted_label = knn_tests(file_path)

            # Pass the uploaded image and the prediction result to the template
            return render_template('knn.html', uploaded_image=filename, prediction=predicted_label)

    return render_template('knn.html')



def process_image(img_processor, choices, img_input, total_cost):
    rgb_image = img_read_helper(img_input) if isinstance(img_input, str) else img_input
    processed_image = rgb_image  # Start with the original image

    for choice in choices:
        if choice == '1':
            processed_image = img_processor.negate(processed_image)
        elif choice == '2':
            processed_image = img_processor.grayscale(processed_image)
        elif choice == '3':
            processed_image = img_processor.rotate_180(processed_image)
        elif choice == '4':
            intensity = int(request.form.get('brightness', 0)) # Get the brightness value
            processed_image = img_processor.adjust_brightness(processed_image, intensity)
        elif choice == '5':
            processed_image = img_processor.blur(processed_image)
        elif choice == '6':  # Chroma Key
            background_image = request.files.get('background_image')
            if background_image:
                background_image_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(background_image.filename))
                background_image.save(background_image_path)

                # Safely get the chroma key color or set a default value
                color_input = request.form.get('chroma_color', '0,0,0')
                color_to_replace = tuple(map(int, color_input.split(',')))

                # Perform chroma key operation
                background_img = img_read_helper(background_image_path)
                processed_image = img_processor.chroma_key(processed_image, background_img, color_to_replace)
            else:
                flash("No background image provided for Chroma Key operation.")
        elif choice == '7':  # Add Sticker
            sticker_image = request.files['sticker_image']  # User uploads a sticker image
            sticker_image_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(sticker_image.filename))
            sticker_image.save(sticker_image_path)
            
            # Extract position data from form input
            x_pos = int(request.form['x_pos'])
            y_pos = int(request.form['y_pos'])
            
            # Perform sticker operation
            sticker_img = img_read_helper(sticker_image_path)
            processed_image = img_processor.sticker(sticker_img, processed_image, x_pos, y_pos)
        elif choice == '8':  # Edge Highlight
            processed_image = img_processor.edge_highlight(processed_image)

    if processed_image:
        new_path = generate_new_filename(img_input, "_processed")
        img_save_helper(new_path, processed_image)
        total_cost += img_processor.get_cost()
        return processed_image, total_cost
    return None

if __name__ == '__main__':
    app.run(debug=True)
