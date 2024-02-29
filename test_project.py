import os
from PIL import Image
import numpy as np
import re
import project
from project import img_read_helper, img_save_helper
from project import StandardImageProcessing, PremiumImageProcessing
from project import ImageKNNClassifier, knn_tests

# Due to univeristy policy, the project file cannot be made publicly available
# but is avilable upon request


OPERATION_COSTS = {
    "1": {"name": "Negate Image", "cost": 5},
    "2": {"name": "Grayscale Image", "cost": 6},
    "3": {"name": "Rotate Image 180°", "cost": 10},
    "4": {"name": "Adjust Brightness", "cost": 1},
    "5": {"name": "Blur Image", "cost": 5}
}

def display_main_menu():
    print("\n")
    print("|--------------------------------|")
    print("|Image Processing App - Main Menu|")
    print("|--------------------------------|\n")
    print("1. Standard Processing  ")
    print("2. Premium Processing")
    print("3. KNN Classifier") 
    print("4. Exit")
    choice = input("Choose an option: ")
    return choice

def display_processing_menu(is_premium=False):
    print("\nSelect Image Processing Operations (Enter 'done' when finished):")
    if is_premium != True:
        for key, value in OPERATION_COSTS.items():
            print(f"{key}. {value['name']} (Cost: ${value['cost']})")
    if is_premium:
        print("6. Premium: Chroma Key")
        print("7. Premium: Add Sticker")
        print("8. Premium: Edge Highlight")
    print("9. Return to Main Menu")
    choices = []
    while True:
        choice = input("\nChoose an operation or 'done': ")
        if choice == 'done' or choice == '9':
            break
        elif choice in OPERATION_COSTS.keys() or \
        (is_premium and choice in ['6', '7', '8']):
            choices.append(choice)
        else:
            print("\nInvalid choice, please enter \
an integer out of the given choices.")
    return choices

def generate_new_filename(original_path, suffix):
    directory, filename = os.path.split(original_path)
    name, extension = os.path.splitext(filename)
    new_filename = f"{name}{suffix}{extension}"
    return os.path.join(directory, new_filename)

def process_image(img_processor, choices, img_input, total_cost):
    # Assuming img_read_helper and img_save_helper are defined elsewhere
    rgb_image = img_read_helper(img_input) if isinstance(img_input, str) \
    else img_input
    processed_image = rgb_image  # Start with the original image

    for choice in choices:
        if choice == '1':
            processed_image = img_processor.negate(processed_image)
        elif choice == '2':
            processed_image = img_processor.grayscale(processed_image)
        elif choice == '3':
            processed_image = img_processor.rotate_180(processed_image)
        elif choice == '4':
            intensity = \
            int(input("\nEnter brightness adjustment (-255 to 255): "))
            processed_image = \
            img_processor.adjust_brightness(processed_image, intensity)
        elif choice == '5':
            processed_image = img_processor.blur(processed_image)
        elif choice == '6':  # Chroma Key
            # Prompt the user for the background image path
            background_image_path = input("Enter the background image path: ")
            if not os.path.exists(background_image_path):
                print("\nBackground file does not exist. Please try again.")
                return
            background_image = img_read_helper(background_image_path)
            
            # Prompt for Chroma Key color
            color_input = input("\nEnter the Chroma Key color to replace \
(in RGB format: R,G,B): ")
            color_parts = color_input.split(',')
            color_parts = [part.strip() for part in color_parts]  
        
            # Validate and convert color parts to integers
            if len(color_parts) == \
            3 & all(part.isdigit() for part in color_parts):
                color_to_replace = tuple(map(int, color_parts))
                try:
                    processed_image = img_processor.chroma_key(processed_image,\
                    background_image, color_to_replace)
                except Exception as e:
                    print(f"\nAn error occurred during the Chroma Key \
operation: {e}")
            else:
                print("\nInvalid color format. Please enter exactly three \
numeric RGB values.")
            

        elif choice == '7':  # Add Sticker
            sticker_image_path = input("Enter the sticker image path: ")
            sticker_image = img_read_helper(sticker_image_path)  
            x_pos = int(input("\nEnter X position for the sticker: "))
            y_pos = int(input("\nEnter Y position for the sticker: "))
            processed_image = img_processor.sticker(sticker_image, \
            processed_image, x_pos, y_pos)  # Apply the sticker
        elif choice == '8':  # Edge Highlight
            processed_image = img_processor.edge_highlight(processed_image)
        else:
            print("\nInvalid choice, please enter an integer \
out of the given options.")
            continue


    if processed_image:
        new_path = generate_new_filename(img_input, "_processed")
        img_save_helper(new_path, processed_image)
        total_cost += img_processor.get_cost()
        print(f"\nProcessed image saved as {new_path}")
        return processed_image, total_cost
    else:
        return None  


def redeem_coupon_ui(processor):
    try:
        amount = int(input("Enter the number of free calls to redeem: "))
        processor.redeem_coupon(amount)
        total_cost = processor.get_cost()
        print(f"\n{amount} free calls redeemed successfully.")
        return total_cost
    except ValueError:
        print("\nInvalid input. Please enter a positive integer.")
    except TypeError:
        print("\nAmount must be an integer.")
    except Exception as e:
        print(f"\nError: {str(e)}")

def knn_classifier_ui():
    test_img_path = input("\nEnter the path to the test image: ")

    if not os.path.exists(test_img_path):
        print("\nError: Test image file does not exist.")
        return

    predicted_label = knn_tests(test_img_path) 
    print(f"\nThe predicted label for the test image is: {predicted_label}")

def run_app():
    processor = None
    total_cost = 0  # Initialize total cost at the start of the app
    premium_selected = False  # Flag to check if premium was selected
    coupon_redeemed = False
    

    while True:
        main_choice = display_main_menu()
        
        if main_choice == '4':  # Exit
            print(f"\nTotal cost for this session: ${total_cost}")
            print("\nExiting application.")
            print("\n")
            break
        
        elif main_choice == '3':  # KNN Classifier
            knn_classifier_ui()  # Handle KNN classifier logic
            continue  # Return to the main menu after classification
            

        if main_choice == '2':  # Premium Processing
            choice = input("A one time $50 will be added to your total cost. \
Would you like to proceed? (yes/no): ").lower()
            if choice == 'yes':
                processor = PremiumImageProcessing()
            else:
                continue

        elif main_choice == '1':  # Standard Processing
            processor = StandardImageProcessing()
            print("\nStandard processing selected.\n")

        if main_choice == 1:
            # Now that a processor is selected, check if user wants to redeem 
            # a coupon
            coupon_choice = input("Do you want to redeem a coupon before\
 proceeding? (yes/no): ").lower()
            if coupon_choice == 'yes':
                redeem_coupon_ui(processor)
                coupon_redeemed = True
            else:
                coupon_redeemed = False


        img_path = input("Enter the path to the image file: ")
        if not os.path.exists(img_path):
            print("\nFile does not exist. Please try again.")
            continue

        operation_choices = display_processing_menu\
(is_premium=(main_choice == '2'))
        for choice in operation_choices:
            if choice in OPERATION_COSTS:
                print(f"\nAdded {OPERATION_COSTS[choice]['name']} for \
                ${OPERATION_COSTS[choice]['cost']}.")
            #Implement the premium operation choices here
        
        processed_image, total_cost = process_image(processor, \
        operation_choices, img_path, total_cost)
        if processed_image:
            print("\nImage processing completed successfully. \
Check your directory!")
        else:
            print("\nAn error occurred during image processing.")

if __name__ == "__main__":
    run_app()


