"""
Huma Case Studies Web Scraper
Scrapes research reports, field reports, and lab reports from humagro.com/case-studies/
"""

import requests
from bs4 import BeautifulSoup
import json
import csv
from datetime import datetime
import time

class HumaScraper:
    def __init__(self):
        self.base_url = "https://humagro.com"
        self.case_studies_url = "https://humagro.com/case-studies/"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        self.reports = []
    
    def fetch_page(self, url):
        """Fetch a web page with error handling"""
        try:
            print(f"Fetching: {url}")
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return None
    
    def categorize_report_type(self, title, description, tags):
        """
        Determine if a report is research, field, or lab based on content
        """
        text = f"{title} {description} {' '.join(tags)}".lower()
        
        # Keywords for each type
        research_keywords = ['research', 'study', 'trial', 'university', 'academic']
        field_keywords = ['field', 'farm', 'grower', 'acre', 'crop', 'yield']
        lab_keywords = ['lab', 'laboratory', 'analysis', 'test']
        
        # Count keyword matches
        research_score = sum(1 for keyword in research_keywords if keyword in text)
        field_score = sum(1 for keyword in field_keywords if keyword in text)
        lab_score = sum(1 for keyword in lab_keywords if keyword in text)
        
        # Determine type based on highest score
        scores = {
            'research': research_score,
            'field': field_score,
            'lab': lab_score
        }
        
        max_score = max(scores.values())
        if max_score == 0:
            return 'field'  # Default to field report if unclear
        
        return max(scores, key=scores.get)
    
    def determine_outcome(self, title, description):
        """
        Determine if report outcome is favorable or unfavorable
        """
        text = f"{title} {description}".lower()
        
        # Positive indicators
        positive_keywords = [
            'increase', 'improve', 'better', 'higher', 'enhanced', 'boost',
            'success', 'positive', 'effective', 'benefit', 'gain', 'growth',
            'superior', 'excellent', 'significant', 'outstanding'
        ]
        
        # Negative indicators
        negative_keywords = [
            'decrease', 'decline', 'lower', 'reduce', 'fail', 'negative',
            'poor', 'worse', 'ineffective', 'loss', 'decline'
        ]
        
        positive_count = sum(1 for keyword in positive_keywords if keyword in text)
        negative_count = sum(1 for keyword in negative_keywords if keyword in text)
        
        if positive_count > negative_count:
            return 'favorable'
        elif negative_count > positive_count:
            return 'unfavorable'
        else:
            return 'favorable'  # Default to favorable for case studies
    
    def scrape_case_studies(self):
        """Main scraping function for Huma case studies page"""
        html = self.fetch_page(self.case_studies_url)
        if not html:
            print("Failed to fetch the main page")
            return []
        
        soup = BeautifulSoup(html, 'html.parser')
        
        # Find all case study cards/links
        # Note: You'll need to inspect the actual HTML structure of the page
        # This is a template that may need adjustment based on the real page structure
        
        # Common patterns to look for:
        case_study_selectors = [
            ('div', {'class': 'case-study'}),
            ('article', {'class': 'post'}),
            ('div', {'class': 'card'}),
            ('div', {'class': 'study'}),
            ('a', {'class': 'case-study-link'}),
        ]
        
        case_studies = []
        for tag, attrs in case_study_selectors:
            found = soup.find_all(tag, attrs)
            if found:
                case_studies.extend(found)
                print(f"Found {len(found)} items with {tag} {attrs}")
        
        # If no specific selectors work, try finding all links
        if not case_studies:
            print("No case studies found with specific selectors, trying all links...")
            all_links = soup.find_all('a', href=True)
            # Filter for links that might be case studies
            case_studies = [
                link for link in all_links 
                if 'case' in link.get('href', '').lower() or 
                   'study' in link.get('href', '').lower() or
                   'research' in link.get('href', '').lower()
            ]
            print(f"Found {len(case_studies)} potential case study links")
        
        print(f"\nProcessing {len(case_studies)} case studies...")
        
        for idx, study in enumerate(case_studies, 1):
            try:
                # Extract basic information
                title = study.get_text(strip=True) if study.name != 'a' else study.get_text(strip=True)
                link = study.get('href', '') if study.name == 'a' else study.find('a').get('href', '')
                
                # Make link absolute if it's relative
                if link and not link.startswith('http'):
                    link = self.base_url + link if link.startswith('/') else f"{self.base_url}/{link}"
                
                # Try to extract description
                description = ""
                desc_elem = study.find(['p', 'div'], class_=['description', 'excerpt', 'summary'])
                if desc_elem:
                    description = desc_elem.get_text(strip=True)
                
                # Extract tags/categories if available
                tags = []
                tag_elems = study.find_all(['span', 'a'], class_=['tag', 'category', 'label'])
                tags = [tag.get_text(strip=True) for tag in tag_elems]
                
                # Categorize the report
                report_type = self.categorize_report_type(title, description, tags)
                outcome = self.determine_outcome(title, description)
                
                report = {
                    'company': 'Huma',
                    'title': title,
                    'url': link,
                    'type': report_type,
                    'description': description,
                    'tags': tags,
                    'outcome': outcome,
                    'isIndependent': False,  # Company website content
                    'source': 'Huma website',
                    'scraped_date': datetime.now().isoformat()
                }
                
                self.reports.append(report)
                print(f"  [{idx}/{len(case_studies)}] {report_type.upper()}: {title[:60]}...")
                
                # Be polite - add a small delay
                time.sleep(0.5)
                
            except Exception as e:
                print(f"Error processing case study {idx}: {e}")
                continue
        
        return self.reports
    
    def analyze_results(self):
        """Print summary statistics"""
        if not self.reports:
            print("\nNo reports found!")
            return
        
        total = len(self.reports)
        research = len([r for r in self.reports if r['type'] == 'research'])
        field = len([r for r in self.reports if r['type'] == 'field'])
        lab = len([r for r in self.reports if r['type'] == 'lab'])
        favorable = len([r for r in self.reports if r['outcome'] == 'favorable'])
        unfavorable = len([r for r in self.reports if r['outcome'] == 'unfavorable'])
        
        print("\n" + "="*60)
        print("SCRAPING SUMMARY")
        print("="*60)
        print(f"Total Reports Found: {total}")
        print(f"  - Research Reports: {research}")
        print(f"  - Field Reports: {field}")
        print(f"  - Lab Reports: {lab}")
        print(f"\nOutcome Analysis:")
        print(f"  - Favorable: {favorable}")
        print(f"  - Unfavorable: {unfavorable}")
        print("="*60 + "\n")
    
    def save_to_json(self, filename='huma_reports.json'):
        """Save reports to JSON file"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.reports, f, indent=2, ensure_ascii=False)
        print(f"Saved {len(self.reports)} reports to {filename}")
    
    def save_to_csv(self, filename='huma_reports.csv'):
        """Save reports to CSV file"""
        if not self.reports:
            print("No reports to save")
            return
        
        keys = ['company', 'title', 'type', 'outcome', 'isIndependent', 'source', 'url', 'description']
        
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=keys, extrasaction='ignore')
            writer.writeheader()
            writer.writerows(self.reports)
        print(f"Saved {len(self.reports)} reports to {filename}")
    
    def generate_import_format(self, filename='huma_import_ready.json'):
        """
        Generate a JSON file formatted for easy import into the tracker app
        """
        import_data = []
        for report in self.reports:
            import_data.append({
                'companyName': report['company'],
                'citationType': report['type'],
                'title': report['title'],
                'source': report['source'],
                'url': report['url'],
                'outcome': report['outcome'],
                'isIndependent': report['isIndependent'],
                'notes': report['description']
            })
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(import_data, f, indent=2, ensure_ascii=False)
        print(f"Generated import-ready file: {filename}")


def main():
    """Main execution function"""
    print("="*60)
    print("HUMA CASE STUDIES SCRAPER")
    print("="*60)
    print("This script will scrape research reports from humagro.com/case-studies/")
    print()
    
    # Create scraper instance
    scraper = HumaScraper()
    
    # Run the scraper
    print("Starting scrape...\n")
    reports = scraper.scrape_case_studies()
    
    # Analyze results
    scraper.analyze_results()
    
    # Save results
    if reports:
        scraper.save_to_json()
        scraper.save_to_csv()
        scraper.generate_import_format()
        
        print("\nSample of first report:")
        print(json.dumps(reports[0], indent=2))
    else:
        print("\n⚠️ No reports were found. This could mean:")
        print("  1. The page structure has changed")
        print("  2. The website is blocking the scraper")
        print("  3. The selectors need to be adjusted")
        print("\nTo fix this, you'll need to:")
        print("  1. Visit https://humagro.com/case-studies/ in your browser")
        print("  2. Right-click and 'Inspect' the page")
        print("  3. Find the HTML elements containing case studies")
        print("  4. Update the 'case_study_selectors' in the code with the correct tags/classes")


if __name__ == "__main__":
    main()
