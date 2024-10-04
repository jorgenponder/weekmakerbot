import mwclient
import pages as pages
import time

sleep_seconds = 6 # Time to sleep between pages uploaded
site_address = 'site.without.schema' # No schema (https://) in the site url
api_path = '/w/' # Adjust the path to where the API is.
bot_name = ''
bot_password = ''

def login(site_address, api_path, bot_name, bot_password):
    site = mwclient.Site(site_address, path=api_path)
    site.login(bot_name, bot_password)
    print(f'Logged in as: {site.credentials[0]}')
    return site

# Create or update pages on the wiki
def upload_pages(site, pages, dry_run):
    if not site.credentials[0]:
        print("Not logged in, aborting.")
        return
    
    for page in pages:
        page_title = page['id']
        page_content = page['body']
        print(f"with title: {page_title}")
        print(f"with body: {page_content}")
        # Get the page object on the wiki
        page = site.pages[page_title]

        if page.exists:
            print(f"Page '{page_title}' already exists. Updating...")
        else:
            print(f"Creating new page: {page_title}")

        # Update the page content
        if not dry_run:
            page.save(page_content, summary=f"Bot created/updated page: {page_title}")
            page.purge()
            print(f"Successfully saved page: {page_title}")
            time.sleep(sleep_seconds) # To not overload the server

# Main function to run the script
if __name__ == "__main__":
    site = login(site_address, api_path, bot_name, bot_password)
    upload_pages(site, pages, dry_run = False)
