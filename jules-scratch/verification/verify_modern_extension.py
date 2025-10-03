import asyncio
from playwright.async_api import async_playwright, expect
import os

async def main():
    """
    This script attempts to test the modernized todolist Firefox extension.
    It loads the extension via about:debugging, opens the popup, adds a task,
    marks it as complete, and verifies the "completed" style.
    """
    extension_path = os.path.abspath('.')

    async with async_playwright() as p:
        browser = await p.firefox.launch(headless=True, slow_mo=50)
        context = await browser.new_context()
        page = await context.new_page()

        try:
            # Navigate to the debugging page to load the extension
            await page.goto("about:debugging#/runtime/this-firefox")

            # Use the file chooser to load the extension
            async with page.expect_file_chooser() as fc_info:
                await page.get_by_role("button", name="Load Temporary Add-on…").click()
            file_chooser = await fc_info.value
            await file_chooser.set_files(os.path.join(extension_path, "manifest.json"))

            # Wait for the extension to be listed and get its ID
            await expect(page.get_by_text("Todolist")).to_be_visible(timeout=10000)

            extension_id_locator = page.locator("dl > dt:has-text('Extension ID') + dd")
            extension_id = await extension_id_locator.inner_text()

            # Construct the URL for the popup
            popup_url = f"moz-extension://{extension_id}/popup/index.html"

            # Open the popup in a new page for testing
            popup_page = await context.new_page()
            await popup_page.goto(popup_url)

            # Verify the modernized UI is present
            await expect(popup_page.get_by_role("heading", name="Todolist")).to_be_visible()

            # Test adding a task
            await popup_page.get_by_placeholder("Enter a new task").fill("Test modern UI")
            await popup_page.get_by_role("button", name="Add").click()

            task_item = popup_page.get_by_text("Test modern UI")
            await expect(task_item).to_be_visible()

            # Test marking the task as complete
            await task_item.click()

            # The task is inside a 'li' element. We expect that 'li' to have the 'completed' class.
            list_item = popup_page.locator("li", has_text="Test modern UI")
            await expect(list_item).to_have_class("completed")

            # Take a screenshot for visual confirmation
            screenshot_path = "jules-scratch/verification/todolist_modern_verification.png"
            await popup_page.screenshot(path=screenshot_path)
            print(f"Screenshot saved to {screenshot_path}")

        except Exception as e:
            print(f"An error occurred during verification: {e}")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(main())