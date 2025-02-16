```
                                                          _ _  _____            _      
                                           /\            (_|_)/ ____|          (_)     
                                          /  \   ___  ___ _ _| |  __  ___ _ __  ___  __
                                         / /\ \ / __|/ __| | | | |_ |/ _ \ '_ \| \ \/ /
                                        / ____ \\__ \ (__| | | |__| |  __/ | | | |>  < 
                                       /_/    \_\___/\___|_|_|\_____|\___|_| |_|_/_/\_\
                                                                                       
```                                                 
                                            
                                                                                  
                                                                                  

This is a **Telegram bot** that converts images into ASCII art using different character sets. It allows users to customize various settings such as width, aspect ratio, contrast, and more.

## Features ✨

- 📷 Convert images to **ASCII art** with different styles.
- ⚙️ **Customizable settings**, including:
  - `new_width` → ASCII output width.
  - `aspect_ratio_adjust` → Adjusts for character proportions.
  - `upscale_factor` → Improves detail by upscaling the image before conversion.
  - `invert` → Inverts the brightness (dark areas become light and vice versa).
  - `gradient_mode` → Choose from different character sets for the ASCII art.

## Commands 🛠️

- `/start` → Starts the bot and provides an introduction.
- `/set` → Customize the settings for ASCII conversion.
- Send an image → Convert it into ASCII art with the current settings.

## Settings Explained ⚙️

1. **new_width**: Defines the width of the ASCII art in characters. The bot automatically calculates the new height based on the image’s aspect ratio and `aspect_ratio_adjust`. Higher values produce more detailed art but can result in larger outputs.

2. **aspect_ratio_adjust**: Adjusts the aspect ratio to compensate for the fact that text characters are taller than they are wide. A lower value results in a more compact output, while a higher value provides better vertical clarity.

3. **upscale_factor**: Determines how much the original image is upscaled before conversion. Increasing this value can help preserve fine details, though it might slow down the conversion process and produce larger outputs.

4. **invert**: Reverses the brightness mapping so that dark areas become light and vice versa. This creates higher contrast in certain images.

5. **gradient_mode**: Defines the set of characters used to create the ASCII art. You can choose from modes like `Default`, `Blocks`, `Classic`, and more.

## Example Output 🎨

After sending an image, the bot will respond with ASCII art in multiple modes, allowing you to compare different styles.

---

Enjoy creating ASCII masterpieces with the bot! ✨
