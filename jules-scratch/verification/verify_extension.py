import asyncio
from playwright.async_api import async_playwright, expect
import os

async def main():
    """
    This script attempts to test the todolist Firefox extension.
    It loads the extension via the about:debugging page, finds its internal UUID,
    opens the popup page directly, and performs a simple test.
    """
    # Get the absolute path to the current directory, which is the extension's root
    extension_path = os.path.abspath('.')

    async with async_playwright() as p:
        # We must launch in non-headless mode for this to work
        browser = await p.firefox.launch(headless=True, slow_mo=50)
        context = await browser.new_context()
        page = await context.new_page()

        try:
            # Navigate to the debugging page to load the extension
            await page.goto("about:debugging#/runtime/this-firefox")

            # Use the file chooser to load the extension
            # This is the step that interacts with the privileged UI
            async with page.expect_file_chooser() as fc_info:
                await page.get_by_role("button", name="Load Temporary Add-on…").click()
            file_chooser = await fc_info.value
            # Selecting the manifest file is enough to load the extension
            await file_chooser.set_files(os.path.join(extension_path, "manifest.json"))

            # Wait for the extension to be listed and get its ID
            await expect(page.get_by_text("Todolist")).to_be_visible(timeout=10000)

            # Find the Extension ID from the details on the page
            extension_id_locator = page.locator("dl > dt:has-text('Extension ID') + dd")
            extension_id = await extension_id_locator.inner_text()

            # Construct the URL for the popup
            popup_url = f"moz-extension://{extension_id}/popup/index.html"

            # Open the popup in a new page for testing
            popup_page = await context.new_page()
            await popup_page.goto(popup_url)

            # Verify the content of the popup
            await expect(popup_page.get_by_role("heading", name="Todolist")).to_be_visible()

            # Test the functionality: add a new task
            await popup_page.get_by_placeholder("Enter a new task").fill("Test the extension")
            await popup_page.get_by_role("button", name="Add").click()

            # Verify that the task was added to the list
            await expect(popup_page.get_by_text("Test the extension")).to_be_visible()

            # Take a screenshot for visual confirmation
            screenshot_path = "jules-scratch/verification/todolist_verification.png"
            await popup_page.screenshot(path=screenshot_path)
            print(f"Screenshot saved to {screenshot_path}")

        except Exception as e:
            print(f"An error occurred during verification: {e}")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(main())