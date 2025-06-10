#!/usr/bin/env python
# coding: utf-8

"""
Publications and Talks from BibTeX
Modified version of academicpages PubsFromBib to handle both publications and talks
"""

from pybtex.database.input import bibtex
import pybtex.database.input.bibtex 
from time import strptime
import string
import html
import os
import re

def clean_field(field_value):
    """Clean BibTeX field values (remove braces, etc.)"""
    if not field_value:
        return ""
    return str(field_value).replace("{", "").replace("}", "").strip()

def format_authors(persons_list):
    """Convert pybtex persons to formatted string"""
    if not persons_list:
        return ""
    
    formatted_authors = []
    for person in persons_list:
        first_names = " ".join(person.first_names)
        last_names = " ".join(person.last_names)
        formatted_authors.append(f"{first_names} {last_names}".strip())
    
    return ", ".join(formatted_authors)

def get_venue(entry):
    """Get appropriate venue field based on entry type"""
    entry_type = entry.original_type.lower()
    fields = entry.fields
    
    if entry_type == 'article':
        return clean_field(fields.get('journal', ''))
    elif entry_type in ['inproceedings', 'conference']:
        return clean_field(fields.get('booktitle', ''))
    elif entry_type == 'incollection':
        book = clean_field(fields.get('booktitle', ''))
        editor = clean_field(fields.get('editor', ''))
        if editor:
            return f"{book} (Ed. {editor})"
        return book
    else:
        return clean_field(fields.get('journal', fields.get('booktitle', '')))

def get_paper_url(entry, bib_id):
    """Get the paper URL, return None if no URL specified"""
    fields = entry.fields
    url = clean_field(fields.get('url', ''))
    
    if url:
        # If URL starts with http, it's external - use as-is
        if url.startswith('http'):
            return url
        # If URL starts with /, it's internal - use as-is
        elif url.startswith('/'):
            return f"http://copotm.github.io{url}"
        # Otherwise assume it's a filename in /files/
        else:
            return f"http://copotm.github.io/files/{url}"
    
    # No URL specified - return None
    return None

def get_download_link(entry, bib_id):
    """Generate download link text, return empty string if no URL"""
    fields = entry.fields
    url = clean_field(fields.get('url', ''))
    
    if url:
        if url.startswith('http'):
            return f"[Access paper here]({url})"
        elif url.startswith('/'):
            return f"[Download paper here](http://copotm.github.io{url})"
        else:
            return f"[Download paper here](http://copotm.github.io/files/{url})"
    
    # No URL - return empty string (no link)
    return ""

def main():
    print("Publications and Talks Generator")
    print("================================")
    
    # Load the bibliography file
    try:
        parser = bibtex.Parser()
        bibdata = parser.parse_file("output.bib")
        print(f"✓ Successfully loaded output.bib")
    except FileNotFoundError:
        print("✗ Error: output.bib not found in current directory")
        print("  Make sure you're running this from the markdown_generator folder")
        return
    except Exception as e:
        print(f"✗ Error parsing BibTeX file: {e}")
        return
    
    # Define what counts as publications vs talks
    PUBLICATION_TYPES = ['article', 'inproceedings', 'incollection', 'book', 'phdthesis', 'mastersthesis']
    TALK_TYPES = ['misc']
    
    # Separate publications and talks
    publications = []
    talks = []
    
    for bib_id in bibdata.entries:
        entry = bibdata.entries[bib_id]
        entry_type = entry.original_type.lower()  # Use original_type instead of entry_type
        if entry_type in PUBLICATION_TYPES:
            publications.append((bib_id, entry))
        elif entry_type in TALK_TYPES:
            talks.append((bib_id, entry))
    
    print(f"Found {len(publications)} publications and {len(talks)} talks")
    
    # Helper functions
    html_escape_table = {
        "&": "&amp;",
        '"': "&quot;",
        "'": "&apos;"
    }
    
    def html_escape(text):
        """Produce entities within text."""
        return "".join(html_escape_table.get(c,c) for c in text)
    
    def clean_field(field_value):
        """Clean BibTeX field values (remove braces, etc.)"""
        if not field_value:
            return ""
        return str(field_value).replace("{", "").replace("}", "").strip()
    
    def format_authors(persons_list):
        """Convert pybtex persons to formatted string"""
        if not persons_list:
            return ""
        
        formatted_authors = []
        for person in persons_list:
            first_names = " ".join(person.first_names)
            last_names = " ".join(person.last_names)
            formatted_authors.append(f"{first_names} {last_names}".strip())
        
        return ", ".join(formatted_authors)
    
    def get_venue(entry):
        """Get appropriate venue field based on entry type"""
        entry_type = entry.original_type.lower()  # Use original_type
        fields = entry.fields
        
        if entry_type == 'article':
            return clean_field(fields.get('journal', ''))
        elif entry_type in ['inproceedings', 'conference']:
            return clean_field(fields.get('booktitle', ''))
        elif entry_type == 'incollection':
            book = clean_field(fields.get('booktitle', ''))
            editor = clean_field(fields.get('editor', ''))
            if editor:
                return f"{book} (Ed. {editor})"
            return book
        else:
            return clean_field(fields.get('journal', fields.get('booktitle', '')))
    
    # Process Publications
    print("\nProcessing publications...")
    
    # Create publications directory if it doesn't exist
    if not os.path.exists("../_publications/"):
        os.makedirs("../_publications/")
        print("Created _publications/ directory")
    
    # Process each publication
    for bib_id, entry in publications:
        fields = entry.fields
        
        # Basic fields
        title = clean_field(fields.get('title', ''))
        authors = format_authors(entry.persons.get('author', []))
        venue = get_venue(entry)
        year = clean_field(fields.get('year', ''))
        
        # Optional fields
        volume = clean_field(fields.get('volume', ''))
        number = clean_field(fields.get('number', ''))
        pages = clean_field(fields.get('pages', ''))
        publisher = clean_field(fields.get('publisher', ''))
        address = clean_field(fields.get('address', ''))
        
        # Build citation string
        citation_parts = [authors]
        
        if year and year.lower() not in ['in press', 'accepted']:
            citation_parts.append(f"({year})")
        elif year:
            citation_parts.append(f"({year})")
        
        citation_parts.append(f'"{title}"')
        
        if venue:
            if entry.original_type.lower() == 'incollection':  # Use original_type
                citation_parts.append(f"In {venue}")
            else:
                citation_parts.append(f"<i>{venue}</i>")
        
        # Add volume/number/pages for articles
        if entry.original_type.lower() == 'article' and (volume or number or pages):  # Use original_type
            vol_info = []
            if volume:
                vol_info.append(volume)
            if number:
                vol_info.append(f"({number})")
            if pages:
                vol_info.append(pages)
            if vol_info:
                citation_parts.append(", ".join(vol_info))
        
        if publisher:
            citation_parts.append(publisher)
        
        citation = ". ".join(citation_parts) + "."
        
        # Create file-safe URL slug
        clean_title_slug = re.sub(r'[^a-zA-Z0-9_-]', '', title.replace(' ', '-').replace('--', '-'))
        url_slug = clean_title_slug[:50]  # Limit length
        
        # Determine date for filename
        if year and year.isdigit():
            pub_date = f"{year}-01-01"
            include_date = True
            is_published = True
        else:
            pub_date = "2099-01-01"  # For filename sorting only
            include_date = False  # Don't show date on website
            is_published = False  # For "in press"/"accepted"
        
        md_filename = f"{pub_date}-{url_slug}.md"
        html_filename = f"{pub_date}-{url_slug}"
        
        # Create markdown content
        paper_url = get_paper_url(entry, bib_id)
        download_link = get_download_link(entry, bib_id)
        
        md_content = f"""---
title: "{title}"
collection: publications
permalink: /publication/{html_filename}"""
        
        # Only add date if it's a real year (not "in press" or "accepted")
        if include_date:
            md_content += f"""
date: {pub_date}"""
        
        md_content += f"""
venue: '{venue}'
published: {str(is_published).lower()}"""
        
        # Only add paperurl if there's a URL
        if paper_url:
            md_content += f"""
paperurl: '{paper_url}'"""
        
        md_content += f"""
citation: '{html_escape(citation)}'
---

{citation}

{download_link}

Recommended citation: {citation}
"""
        
        # Write the file
        try:
            with open(f"../_publications/{md_filename}", 'w', encoding='utf-8') as f:
                f.write(md_content)
            print(f"  ✓ Created {md_filename}")
        except Exception as e:
            print(f"  ✗ Error creating {md_filename}: {e}")
    
    print(f"Processed {len(publications)} publications")
    
    # Process Talks
    print("\nProcessing talks...")
    
    # Create talks directory if it doesn't exist
    if not os.path.exists("../_talks/"):
        os.makedirs("../_talks/")
        print("Created _talks/ directory")
    
    def get_talk_venue(entry):
        """Get venue information for talks"""
        fields = entry.fields
        howpublished = clean_field(fields.get('howpublished', ''))
        address = clean_field(fields.get('address', ''))
        organization = clean_field(fields.get('organization', ''))
        
        venue_parts = []
        if howpublished:
            venue_parts.append(howpublished)
        if organization and organization not in howpublished:
            venue_parts.append(organization)
        if address:
            venue_parts.append(address)
        
        return ", ".join(venue_parts)
    
    def get_talk_type(entry):
        """Determine talk type from note field"""
        fields = entry.fields
        note = clean_field(fields.get('note', '')).lower()
        if 'invited' in note:
            return 'Invited Talk'
        elif 'internal' in note:
            return 'Internal Talk'
        else:
            return 'Conference Talk'
    
    # Process each talk
    for bib_id, entry in talks:
        fields = entry.fields
        
        # Basic fields
        title = clean_field(fields.get('title', ''))
        authors = format_authors(entry.persons.get('author', []))
        venue = get_talk_venue(entry)
        talk_type = get_talk_type(entry)
        year = clean_field(fields.get('year', ''))
        location = clean_field(fields.get('address', ''))
        
        # Determine date for filename
        if year and year.isdigit():
            talk_date = f"{year}-01-01"
        else:
            talk_date = "2099-01-01"
        
        # Create file-safe URL slug
        clean_title_slug = re.sub(r'[^a-zA-Z0-9_-]', '', title.replace(' ', '-').replace('--', '-'))
        url_slug = clean_title_slug[:50]  # Limit length
        
        md_filename = f"{talk_date}-{url_slug}.md"
        html_filename = f"{talk_date}-{url_slug}"
        
        # Create markdown content
        md_content = f"""---
title: "{title}"
collection: talks
type: "{talk_type}"
permalink: /talks/{html_filename}
venue: "{venue}"
date: {talk_date}
location: "{location}"
---

{title}

Given at {venue} ({year}).
"""
        
        # Write the file
        try:
            with open(f"../_talks/{md_filename}", 'w', encoding='utf-8') as f:
                f.write(md_content)
            print(f"  ✓ Created {md_filename}")
        except Exception as e:
            print(f"  ✗ Error creating {md_filename}: {e}")
    
    print(f"Processed {len(talks)} talks")
    
    print("\nSummary:")
    print(f"✓ Created {len(publications)} publication files in _publications/")
    print(f"✓ Created {len(talks)} talk files in _talks/")
    print("\nNext steps:")
    print("1. Review the generated files and edit excerpts, dates, etc.")
    print("2. Add PDF files to /files/ directory")
    print("3. Update paperurl fields if PDFs have different names")
    print("4. Customize the markdown content as needed")

if __name__ == "__main__":
    main()