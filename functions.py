import pandas as pd

# Function to add a company to database
def add_company(company, website, research, lab, field, testimonials, news, sentiment):
    global df
    
    total = research + lab + field + testimonials
    
    new_row = {
        'company': company,
        'website': website,
        'total_citations': total,
        'research_reports': research,
        'lab_reports': lab,
        'field_reports': field,
        'testimonials': testimonials,
        'news_articles': news,
        'news_sentiment': sentiment
    }
    
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    print(f"✓ Added {company}")
    return df


# update a single row
# Example:
# update_company('AcmeCorp', research_reports=15, news_articles=10)
def update_company(company_name, **kwargs):
    
    global df
    
    if company_name not in df['company'].values:
        print(f"✗ Company '{company_name}' not found!")
        return df
    
    idx = df[df['company'] == company_name].index[0]
    
    for key, value in kwargs.items():
        if key in df.columns:
            df.at[idx, key] = value
    
    # Recalculate total_citations if citation columns were updated
    citation_cols = ['research_reports', 'lab_reports', 'field_reports', 'testimonials']
    if any(col in kwargs for col in citation_cols):
        df.at[idx, 'total_citations'] = df.loc[idx, citation_cols].sum()
    
    print(f"✓ Updated {company_name}")
    return df

# total citations should add up
# company names should be unique
# sentiment values should be binary
def validate_data():
    issues = []
    
    # Check if total_citations matches sum
    df['calculated_total'] = (df['research_reports'] + df['lab_reports'] + 
                               df['field_reports'] + df['testimonials'])
    
    mismatches = df[df['total_citations'] != df['calculated_total']]
    if not mismatches.empty:
        issues.append(f"Total citation mismatches found in {len(mismatches)} rows")
        print("⚠ WARNING: Total citations don't match calculated sum:")
        print(mismatches[['company', 'total_citations', 'calculated_total']])
    
    # Check for duplicate companies
    duplicates = df[df.duplicated(subset=['company'], keep=False)]
    if not duplicates.empty:
        issues.append(f"Duplicate companies found: {len(duplicates)} rows")
        print("⚠ WARNING: Duplicate companies found:")
        print(duplicates['company'])
    
    # Check for invalid sentiment values
    valid_sentiments = ['favorable', 'unfavorable']
    invalid_sentiments = df[~df['news_sentiment'].isin(valid_sentiments)]
    if not invalid_sentiments.empty:
        issues.append(f"Invalid sentiment values: {len(invalid_sentiments)} rows")
        print("⚠ WARNING: Invalid sentiment values:")
        print(invalid_sentiments[['company', 'news_sentiment']])
    
    if not issues:
        print("✓ Data validation passed! No issues found.")
    
    # Drop temporary column
    df.drop('calculated_total', axis=1, inplace=True)
    
    return len(issues) == 0

# save
def save_data(filename='data.csv'):
    """Save the current dataframe to CSV"""
    df.to_csv(filename, index=False)
    print(f"\n✓ Data saved to {filename}")
    print(f"  Total rows: {len(df)}")
    print(f"  Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")