-- =============================================================================
-- DealSense AI — Sample Seed Data
-- 50 high-profile M&A deals + 30 news articles for demo/testing
-- =============================================================================

-- =============================================================================
-- DIM_COMPANIES seed
-- =============================================================================

INSERT INTO mart.dim_companies (company_name, ticker, sector, industry, country, is_acquirer, is_target, total_deals, total_deal_value, success_rate) VALUES
('Microsoft', 'MSFT', 'Technology', 'Software', 'USA', TRUE, FALSE, 28, 85000000000, 0.78),
('GitHub', NULL, 'Technology', 'Software', 'USA', FALSE, TRUE, 0, 0, NULL),
('Adobe', 'ADBE', 'Technology', 'Software', 'USA', TRUE, FALSE, 8, 25000000000, 0.75),
('Figma', NULL, 'Technology', 'Design Software', 'USA', FALSE, TRUE, 0, 0, NULL),
('Salesforce', 'CRM', 'Technology', 'Software', 'USA', TRUE, FALSE, 22, 45000000000, 0.68),
('Slack', NULL, 'Technology', 'Enterprise Software', 'USA', FALSE, TRUE, 0, 0, NULL),
('Alphabet', 'GOOGL', 'Technology', 'Internet', 'USA', TRUE, FALSE, 15, 35000000000, 0.73),
('Mandiant', NULL, 'Technology', 'Cybersecurity', 'USA', FALSE, TRUE, 0, 0, NULL),
('Warner Bros', 'WBD', 'Media', 'Entertainment', 'USA', TRUE, FALSE, 4, 8500000000, 0.65),
('Discovery', 'DISCA', 'Media', 'Entertainment', 'USA', FALSE, TRUE, 0, 0, NULL),
('AT&T', 'T', 'Telecom', 'Telecom', 'USA', TRUE, FALSE, 6, 12000000000, 0.60),
('Time Warner', NULL, 'Media', 'Entertainment', 'USA', FALSE, TRUE, 0, 0, NULL),
('Disney', 'DIS', 'Media', 'Entertainment', 'USA', TRUE, FALSE, 12, 75000000000, 0.72),
('21st Century Fox', NULL, 'Media', 'Entertainment', 'USA', FALSE, TRUE, 0, 0, NULL),
('Amazon', 'AMZN', 'Consumer', 'E-commerce', 'USA', TRUE, FALSE, 18, 20000000000, 0.80),
('Whole Foods', NULL, 'Retail', 'Grocery', 'USA', FALSE, TRUE, 0, 0, NULL),
('Walmart', 'WMT', 'Retail', 'Retail', 'USA', TRUE, FALSE, 14, 15000000000, 0.75),
('Flipkart', NULL, 'Retail', 'E-commerce', 'India', FALSE, TRUE, 0, 0, NULL),
('Meta', 'META', 'Technology', 'Social Media', 'USA', TRUE, FALSE, 11, 30000000000, 0.82),
('Instagram', NULL, 'Technology', 'Social Media', 'USA', FALSE, TRUE, 0, 0, NULL),
('WhatsApp', NULL, 'Technology', 'Messaging', 'USA', FALSE, TRUE, 0, 0, NULL),
('Apple', 'AAPL', 'Technology', 'Consumer Electronics', 'USA', TRUE, FALSE, 10, 8000000000, 0.70),
('Beats', NULL, 'Technology', 'Audio', 'USA', FALSE, TRUE, 0, 0, NULL),
('IBM', 'IBM', 'Technology', 'Enterprise Software', 'USA', TRUE, FALSE, 20, 20000000000, 0.65),
('Red Hat', NULL, 'Technology', 'Open Source Software', 'USA', FALSE, TRUE, 0, 0, NULL),
('Broadcom', 'AVGO', 'Semiconductors', 'Semiconductors', 'USA', TRUE, FALSE, 9, 65000000000, 0.77),
('VMware', NULL, 'Technology', 'Virtualization', 'USA', FALSE, TRUE, 0, 0, NULL),
('Nvidia', 'NVDA', 'Semiconductors', 'AI/Chips', 'USA', TRUE, FALSE, 5, 4000000000, 0.85),
('Arm', NULL, 'Technology', 'Semiconductor IP', 'UK', FALSE, TRUE, 0, 0, NULL),
('SAP', 'SAP', 'Technology', 'Enterprise Software', 'Germany', TRUE, FALSE, 12, 15000000000, 0.72),
('Qualtrics', NULL, 'Technology', 'Survey Software', 'USA', FALSE, TRUE, 0, 0, NULL),
('Snowflake', 'SNOW', 'Technology', 'Cloud Data', 'USA', TRUE, FALSE, 4, 2000000000, 0.80),
('RoboMQ', NULL, 'Technology', 'Integration Software', 'USA', FALSE, TRUE, 0, 0, NULL),
('Cisco', 'CSCO', 'Technology', 'Networking', 'USA', TRUE, FALSE, 25, 30000000000, 0.73),
('Splunk', NULL, 'Technology', 'Data Analytics', 'USA', FALSE, TRUE, 0, 0, NULL),
('Google', 'GOOG', 'Technology', 'Internet', 'USA', TRUE, FALSE, 12, 25000000000, 0.78),
('Mandiant', NULL, 'Technology', 'Cybersecurity', 'USA', FALSE, TRUE, 0, 0, NULL),
('HP', 'HPQ', 'Technology', 'Computing', 'USA', TRUE, FALSE, 7, 12000000000, 0.68),
('Poly', NULL, 'Technology', 'Audio/Video', 'USA', FALSE, TRUE, 0, 0, NULL),
('Amgen', 'AMGN', 'Healthcare', 'Biotech', 'USA', TRUE, FALSE, 6, 25000000000, 0.70),
('Horizon Therapeutics', NULL, 'Healthcare', 'Biotech', 'Ireland', FALSE, TRUE, 0, 0, NULL)
ON CONFLICT (company_name, ticker) DO NOTHING;

-- =============================================================================
-- DIM_INDUSTRIES seed
-- =============================================================================

INSERT INTO mart.dim_industries (industry_name, sector, avg_deal_size, avg_premium, historical_count, success_rate, avg_ev_revenue, avg_ev_ebitda) VALUES
('Software', 'Technology', 8500000000, 0.35, 450, 0.72, 8.5, 22.0),
('Design Software', 'Technology', 15000000000, 0.50, 30, 0.65, 15.0, 40.0),
('Enterprise Software', 'Technology', 6000000000, 0.32, 380, 0.68, 7.2, 18.5),
('Cybersecurity', 'Technology', 4000000000, 0.38, 120, 0.75, 9.0, 25.0),
('Entertainment', 'Media', 12000000000, 0.28, 200, 0.65, 3.5, 12.0),
('Telecom', 'Telecom', 8000000000, 0.22, 150, 0.60, 3.0, 10.0),
('E-commerce', 'Consumer', 5000000000, 0.40, 300, 0.78, 6.0, 20.0),
('Grocery', 'Retail', 12000000000, 0.40, 80, 0.55, 1.5, 12.0),
('Social Media', 'Technology', 15000000000, 0.45, 100, 0.70, 12.0, 35.0),
('Messaging', 'Technology', 19000000000, 0.60, 40, 0.72, 18.0, 45.0),
('Consumer Electronics', 'Technology', 3000000000, 0.30, 150, 0.68, 3.0, 15.0),
('Audio', 'Technology', 3000000000, 0.55, 60, 0.75, 5.0, 18.0),
('Open Source Software', 'Technology', 7000000000, 0.42, 90, 0.73, 8.0, 25.0),
('Semiconductors', 'Semiconductors', 15000000000, 0.35, 180, 0.75, 6.0, 18.0),
('Semiconductor IP', 'Technology', 40000000000, 0.40, 20, 0.80, 30.0, 60.0),
('Cloud Data', 'Technology', 5000000000, 0.48, 60, 0.82, 20.0, 50.0),
('Data Analytics', 'Technology', 20000000000, 0.38, 100, 0.70, 10.0, 28.0),
('Internet', 'Technology', 10000000000, 0.36, 250, 0.74, 7.0, 22.0),
('Networking', 'Technology', 8000000000, 0.30, 200, 0.71, 5.5, 16.0),
('Computing', 'Technology', 4000000000, 0.28, 120, 0.68, 4.0, 14.0),
('Audio/Video', 'Technology', 2000000000, 0.33, 80, 0.72, 3.5, 12.0),
('Biotech', 'Healthcare', 15000000000, 0.40, 250, 0.68, 8.0, 20.0)
ON CONFLICT (industry_name) DO NOTHING;

-- =============================================================================
-- RAW.MA_DEALS seed — 50 major M&A transactions
-- =============================================================================

INSERT INTO raw.ma_deals (acquirer, target, industry, deal_value_usd, announcement_date, closing_date, deal_status, ev_revenue, ev_ebitda, premium_paid, revenue_usd, ebitda_usd, synergy_revenue_usd, synergy_cost_usd, integration_cost_usd, deal_success, post_merger_performance, source_url)
VALUES
-- Tech Mega-Deals
('Microsoft', 'GitHub', 'Software', 7500000000, '2018-06-04', '2018-10-26', 'completed', 45.0, 120.0, 0.49, 300000000, 100000000, 200000000, 150000000, 50000000, TRUE, 0.85, 'https://news.microsoft.com'),
('Adobe', 'Figma', 'Design Software', 20000000000, '2022-09-15', '2023-12-18', 'pending', 50.0, 200.0, 0.50, 400000000, 100000000, 500000000, 300000000, 800000000, NULL, NULL, 'https://news.adobe.com'),
('Salesforce', 'Slack', 'Enterprise Software', 27700000000, '2020-12-01', '2021-07-21', 'completed', 24.0, 65.0, 0.38, 1200000000, 450000000, 600000000, 400000000, 600000000, TRUE, 0.55, 'https://salesforce.com'),
('Alphabet', 'Mandiant', 'Cybersecurity', 5400000000, '2022-03-08', '2022-09-12', 'completed', 12.5, 35.0, 0.33, 450000000, 150000000, 200000000, 100000000, 80000000, TRUE, 0.72, 'https://abc.xyz'),
('Warner Bros Discovery', 'WarnerMedia', 'Entertainment', 43000000000, '2022-04-08', '2022-04-08', 'completed', 3.0, 10.0, 0.20, 15000000000, 4000000000, 3000000000, 2000000000, 1500000000, FALSE, -0.15, 'https://wbd.com'),
('AT&T', 'Time Warner', 'Entertainment', 85400000000, '2016-10-23', '2018-06-15', 'completed', 5.0, 12.0, 0.22, 18000000000, 7000000000, 1000000000, 800000000, 1200000000, FALSE, -0.25, 'https://att.com'),
('Disney', '21st Century Fox', 'Entertainment', 71300000000, '2017-12-14', '2019-03-20', 'completed', 3.5, 13.0, 0.28, 21000000000, 5500000000, 2000000000, 1500000000, 2000000000, TRUE, 0.10, 'https://disney.com'),
('Amazon', 'Whole Foods', 'Grocery', 13700000000, '2017-06-16', '2017-08-23', 'completed', 1.0, 12.0, 0.27, 16000000000, 1200000000, 0, 500000000, 500000000, TRUE, 0.20, 'https://amazon.com'),
('Walmart', 'Flipkart', 'E-commerce', 16000000000, '2018-05-09', '2018-08-09', 'completed', 5.0, 40.0, 0.15, 4600000000, 400000000, 100000000, 300000000, 400000000, TRUE, 0.45, 'https://walmart.com'),
('Meta', 'Instagram', 'Social Media', 1000000000, '2012-04-09', '2012-08-23', 'completed', 20.0, 80.0, 0.55, 100000000, 0, 0, 0, 10000000, TRUE, 1.50, 'https://meta.com'),
('Meta', 'WhatsApp', 'Messaging', 19000000000, '2014-02-19', '2014-10-06', 'completed', 60.0, 200.0, 0.60, 1000000000, 0, 300000000, 200000000, 500000000, TRUE, 0.30, 'https://meta.com'),
('Apple', 'Beats', 'Audio', 3000000000, '2014-05-28', '2014-08-01', 'completed', 12.0, 50.0, 0.55, 1000000000, 0, 100000000, 50000000, 100000000, TRUE, 0.25, 'https://apple.com'),
('IBM', 'Red Hat', 'Open Source Software', 34000000000, '2018-10-29', '2019-07-09', 'completed', 10.0, 35.0, 0.42, 3400000000, 900000000, 800000000, 500000000, 400000000, TRUE, 0.15, 'https://ibm.com'),
('Broadcom', 'VMware', 'Virtualization', 61000000000, '2022-05-26', '2022-11-22', 'completed', 14.0, 30.0, 0.40, 13000000000, 2000000000, 1000000000, 800000000, 600000000, TRUE, 0.08, 'https://broadcom.com'),
('Nvidia', 'Arm', 'Semiconductor IP', 40000000000, '2020-09-13', NULL, 'failed', 45.0, 80.0, 0.40, 2000000000, 500000000, 500000000, 400000000, 1000000000, FALSE, NULL, 'https://nvidia.com'),
('SAP', 'Qualtrics', 'Survey Software', 8000000000, '2019-11-11', '2021-01-27', 'completed', 20.0, 60.0, 0.48, 800000000, 150000000, 100000000, 80000000, 150000000, TRUE, 0.65, 'https://sap.com'),
('Snowflake', 'RoboMQ', 'Integration Software', 560000000, '2020-09-15', '2021-01-06', 'completed', 28.0, 80.0, 0.35, 200000000, 0, 20000000, 10000000, 15000000, TRUE, 0.80, 'https://snowflake.com'),
('Cisco', 'Splunk', 'Data Analytics', 20000000000, '2024-09-20', NULL, 'pending', 10.0, 28.0, 0.38, 3500000000, 500000000, 300000000, 200000000, 400000000, NULL, NULL, 'https://cisco.com'),
('HP', 'Poly', 'Audio/Video', 3300000000, '2023-03-01', '2023-08-01', 'completed', 2.5, 10.0, 0.33, 1200000000, 300000000, 100000000, 80000000, 200000000, TRUE, 0.12, 'https://hp.com'),
('Amgen', 'Horizon Therapeutics', 'Biotech', 27800000000, '2022-12-12', '2023-10-06', 'completed', 18.0, 35.0, 0.40, 6000000000, 800000000, 400000000, 300000000, 500000000, TRUE, -0.05, 'https://amgen.com'),
-- Additional historical deals for training data
('Microsoft', 'LinkedIn', 'Enterprise Software', 26200000000, '2016-06-13', '2016-12-08', 'completed', 8.5, 22.0, 0.50, 3000000000, 1200000000, 300000000, 500000000, 400000000, TRUE, 0.18, 'https://microsoft.com'),
('Microsoft', 'Nuance', 'Healthcare AI', 19700000000, '2021-04-12', '2022-03-04', 'completed', 12.0, 30.0, 0.23, 1500000000, 600000000, 200000000, 150000000, 300000000, TRUE, 0.35, 'https://microsoft.com'),
('Adobe', 'Marketo', 'Marketing Software', 4750000000, '2018-09-20', '2018-11-21', 'completed', 9.0, 25.0, 0.35, 500000000, 150000000, 100000000, 80000000, 100000000, TRUE, 0.28, 'https://adobe.com'),
('Salesforce', 'Tableau', 'Data Visualization', 15700000000, '2019-06-10', '2019-08-01', 'completed', 14.0, 40.0, 0.42, 1200000000, 400000000, 150000000, 200000000, 250000000, TRUE, 0.40, 'https://salesforce.com'),
('Salesforce', 'MuleSoft', 'Integration', 6500000000, '2018-03-20', '2018-05-31', 'completed', 10.0, 35.0, 0.38, 700000000, 200000000, 100000000, 80000000, 120000000, TRUE, 0.45, 'https://salesforce.com'),
('Google', 'Fitbit', 'Wearables', 2100000000, '2019-11-01', '2021-01-14', 'completed', 6.0, 25.0, 0.30, 1800000000, 300000000, 100000000, 80000000, 200000000, TRUE, -0.05, 'https://google.com'),
('Google', 'DoubleClick', 'Advertising', 3100000000, '2008-03', '2008-04', 'completed', 12.0, 35.0, 0.45, 1000000000, 0, 200000000, 100000000, 150000000, TRUE, 0.60, 'https://google.com'),
('Facebook', 'Oculus', 'VR', 2000000000, '2014-03-25', '2014-07-21', 'completed', 15.0, NULL, 0.60, 500000000, 0, 50000000, 30000000, 100000000, TRUE, 0.20, 'https://meta.com'),
('Amazon', 'Zappos', 'E-commerce', 1200000000, '2009-07', '2009-11', 'completed', 2.0, 15.0, 0.40, 1000000000, 0, 50000000, 30000000, 80000000, TRUE, 0.50, 'https://amazon.com'),
('Amazon', 'Ring', 'Smart Home', 1000000000, '2018-02-27', '2018-04-12', 'completed', 8.0, 30.0, 0.55, 400000000, 0, 30000000, 20000000, 60000000, TRUE, 0.55, 'https://amazon.com'),
('Disney', 'Pixar', 'Entertainment', 7400000000, '2006-01-24', '2006-05-05', 'completed', 12.0, 35.0, 0.28, 2800000000, 300000000, 200000000, 150000000, 300000000, TRUE, 0.80, 'https://disney.com'),
('Disney', 'Marvel', 'Entertainment', 4000000000, '2009-08-31', '2009-12-31', 'completed', 5.0, 18.0, 0.25, 2000000000, 200000000, 100000000, 80000000, 150000000, TRUE, 1.20, 'https://disney.com'),
('Disney', 'Lucasfilm', 'Entertainment', 4050000000, '2012-10-30', '2012-12-21', 'completed', 6.0, 20.0, 0.22, 1800000000, 150000000, 80000000, 60000000, 120000000, TRUE, 0.90, 'https://disney.com'),
('Walmart', 'Jet.com', 'E-commerce', 3300000000, '2016-08-08', '2016-09-19', 'completed', 4.0, 30.0, 0.38, 1300000000, 0, 100000000, 150000000, 200000000, FALSE, -0.30, 'https://walmart.com'),
('Microsoft', 'Nokia Devices', 'Mobile', 7200000000, '2013-09-03', '2014-04-25', 'completed', 0.8, 8.0, 0.18, 30000000000, 1000000000, 100000000, 500000000, 1500000000, FALSE, -0.60, 'https://microsoft.com'),
('Microsoft', 'Activision Blizzard', 'Gaming', 69000000000, '2022-01-18', '2023-10-13', 'completed', 8.0, 22.0, 0.35, 8800000000, 2500000000, 1000000000, 800000000, 1200000000, TRUE, 0.15, 'https://microsoft.com'),
('Amazon', 'MGM', 'Entertainment', 8450000000, '2021-05-26', '2022-03-15', 'completed', 3.5, 12.0, 0.27, 4000000000, 700000000, 200000000, 150000000, 300000000, TRUE, 0.22, 'https://amazon.com'),
('Visa', 'Plaid', 'Fintech', 5300000000, '2020-01-13', NULL, 'failed', 25.0, 60.0, 0.45, 400000000, 0, 50000000, 40000000, 150000000, FALSE, NULL, 'https://visa.com'),
('Brown-Forman', 'Jose Cuervo', 'Beverages', 4200000000, '2021-06-04', NULL, 'failed', 8.0, 20.0, 0.20, 900000000, 200000000, 80000000, 100000000, 200000000, FALSE, NULL, 'https://brown-foreman.com'),
('UnitedHealth', 'Change Healthcare', 'Healthcare Tech', 7800000000, '2021-01-21', NULL, 'failed', 4.0, 15.0, 0.30, 15000000000, 1500000000, 300000000, 200000000, 500000000, FALSE, NULL, 'https://unitedhealth.com'),
('Google', 'YouTube', 'Internet Video', 1650000000, '2006-10-09', '2006-11-13', 'completed', 18.0, 50.0, 0.60, 250000000, 0, 100000000, 50000000, 100000000, TRUE, 2.50, 'https://google.com'),
('Comcast', 'NBCUniversal', 'Media', 6500000000, '2009-12-03', '2011-01-28', 'completed', 2.5, 9.0, 0.20, 12000000000, 2000000000, 500000000, 400000000, 600000000, TRUE, 0.10, 'https://comcast.com'),
('Verizon', 'Yahoo', 'Internet', 4800000000, '2016-07-25', '2017-06-13', 'completed', 5.0, 18.0, 0.22, 5000000000, 400000000, 100000000, 200000000, 300000000, FALSE, -0.35, 'https://verizon.com'),
('Verizon', 'AOL', 'Internet', 4400000000, '2015-05-12', '2015-06-23', 'completed', 3.0, 12.0, 0.38, 3500000000, 300000000, 80000000, 100000000, 250000000, FALSE, -0.25, 'https://verizon.com'),
('Exxon', 'Mobil', 'Energy', 80000000000, '1998-12-01', '1999-11-30', 'completed', 2.0, 8.0, 0.15, 200000000000, 15000000000, 5000000000, 3000000000, 2000000000, TRUE, 0.08, 'https://exxon.com'),
('BP', 'Arco', 'Energy', 5400000000, '1999-04-01', '2000-04-01', 'completed', 1.5, 7.0, 0.20, 8000000000, 500000000, 200000000, 150000000, 300000000, TRUE, 0.12, 'https://bp.com'),
('CVS', 'Aetna', 'Healthcare', 69000000000, '2017-12-03', '2018-11-28', 'completed', 2.5, 11.0, 0.32, 20000000000, 5000000000, 1000000000, 800000000, 1200000000, TRUE, -0.02, 'https://cvs.com'),
('UnitedHealth', 'Optum', 'Healthcare', 5200000000, '2011-07-22', '2011-10-19', 'completed', 3.0, 10.0, 0.28, 2800000000, 800000000, 300000000, 200000000, 400000000, TRUE, 0.30, 'https://unitedhealth.com'),
('Oracle', 'Sun Microsystems', 'Technology', 7400000000, '2009-04-20', '2010-01-27', 'completed', 3.5, 15.0, 0.35, 13000000000, 1500000000, 400000000, 500000000, 800000000, FALSE, -0.15, 'https://oracle.com'),
('Oracle', 'NetSuite', 'Enterprise Software', 9300000000, '2016-07-28', '2016-11-04', 'completed', 8.0, 25.0, 0.38, 1200000000, 300000000, 100000000, 80000000, 150000000, TRUE, 0.40, 'https://oracle.com'),
('Microsoft', 'Visio', 'Productivity', 1375000000, '2000-01-07', '2000-01-26', 'completed', 10.0, 35.0, 0.50, 500000000, 0, 30000000, 20000000, 60000000, TRUE, 0.55, 'https://microsoft.com')
ON CONFLICT DO NOTHING;

-- =============================================================================
-- RAW.NEWS_ARTICLES seed — 30 articles for sentiment analysis training
-- =============================================================================

INSERT INTO raw.news_articles (title, content, source, author, published_at, url, sentiment_score, sentiment_label, company_tag, industry_tag)
VALUES
('Microsoft Reports Strong Cloud Growth Post-GitHub Acquisition', 'Microsoft Azure and GitHub integration driving enterprise DevOps adoption at record levels.', 'Reuters', 'Sarah Chen', '2024-01-15 10:00:00', 'https://reuters.com/microsoft-github-2024', 0.82, 'positive', 'Microsoft', 'Software'),
('Adobe-Figma Deal Faces EU Regulatory Scrutiny', 'European Commission opens in-depth investigation into design software market concentration.', 'Bloomberg', 'Hans Mueller', '2023-03-15 08:30:00', 'https://bloomberg.com/adobe-figma-eu', -0.45, 'negative', 'Adobe', 'Design Software'),
('Salesforce-Slack Integration Delivers Synergy Upside', 'Q4 results show CRM platform expansion driving cross-sell growth beyond projections.', 'WSJ', 'Emily Watson', '2024-02-10 09:00:00', 'https://wsj.com/salesforce-slack-synergy', 0.68, 'positive', 'Salesforce', 'Enterprise Software'),
('Tech M&A Activity Hits Five-Year Low Amid Rate Concerns', 'Interest rate environment weighing on deal valuations, with multiple transactions terminated.', 'Financial Times', 'James Morrison', '2024-01-20 11:00:00', 'https://ft.com/tech-ma-slowdown', -0.62, 'negative', NULL, 'Software'),
('Google Mandiant Integration Strengthens Enterprise Security Portfolio', 'Cybersecurity offerings expand with managed detection and response capabilities.', 'TechCrunch', 'Alex Rodriguez', '2024-03-01 14:00:00', 'https://techcrunch.com/google-mandiant', 0.75, 'positive', 'Alphabet', 'Cybersecurity'),
('Warner Bros Discovery Streaming Losses Continue', 'Combined entity reports challenging subscriber growth and content amortization charges.', 'Variety', 'Michael Lee', '2024-01-25 16:00:00', 'https://variety.com/wbd-losses', -0.55, 'negative', 'Warner Bros', 'Entertainment'),
('Disney Streaming Profitability Milestone Reached', 'House of Mouse reports first profitable quarter for Disney+ streaming division.', 'CNBC', 'Jessica Park', '2024-02-08 12:00:00', 'https://cnbc.com/disney-streaming-profit', 0.70, 'positive', 'Disney', 'Entertainment'),
('Amazon Whole Foods Price Cuts Drive Market Share Gains', 'Grocer competitive landscape shifts with Amazon pricing strategy.', 'Wall Street Journal', 'Robert Kim', '2023-12-01 10:00:00', 'https://wsj.com/amazon-whole-foods', 0.42, 'positive', 'Amazon', 'Grocery'),
('Nvidia Arm Deal Collapse Leaves Chip Industry Reeling', 'Regulatory opposition on three continents ends $40B transaction.', 'The Verge', 'Dieter Bohn', '2022-02-08 09:00:00', 'https://theverge.com/nvidia-arm-failed', -0.78, 'negative', 'Nvidia', 'Semiconductor IP'),
('IBM Red Hat Hybrid Cloud Momentum Continues', 'Enterprise open-source adoption driving consistent growth in recurring revenue.', 'Forbes', 'Sarah Johnson', '2024-02-22 08:00:00', 'https://forbes.com/ibm-red-hat-growth', 0.65, 'positive', 'IBM', 'Open Source Software'),
('Broadcom VMware Integration on Track', 'Enterprise virtualization leadership driving infrastructure software expansion.', 'Reuters', 'Mark Thompson', '2024-01-30 11:00:00', 'https://reuters.com/broadcom-vmware', 0.58, 'positive', 'Broadcom', 'Virtualization'),
('Amgen Horizon Deal Faces Antitrust Challenges', 'FTC scrutiny of rare disease drug portfolio creates deal uncertainty.', 'Stat News', 'Casey Ross', '2023-06-15 09:00:00', 'https://statnews.com/amgen-horizon', -0.35, 'negative', 'Amgen', 'Biotech'),
('Walmart E-commerce Profitability Improves', 'Flipkart integration and fulfillment optimization driving margin expansion.', 'Bloomberg', 'Priya Sharma', '2024-02-05 13:00:00', 'https://bloomberg.com/walmart-ecommerce', 0.52, 'positive', 'Walmart', 'E-commerce'),
('Meta AI Investment Drives Advertiser Return', 'Instagram and Facebook ad measurement improvements boost brand spending.', 'AdWeek', 'Lisa Chang', '2024-02-14 10:00:00', 'https://adweek.com/meta-ai-ads', 0.48, 'positive', 'Meta', 'Social Media'),
('Cisco Splunk Cybersecurity Platform Launches', 'AI-powered security analytics transforms enterprise threat detection.', 'Dark Reading', 'Michael Torres', '2024-03-10 15:00:00', 'https://darkreading.com/cisco-splunk', 0.73, 'positive', 'Cisco', 'Data Analytics'),
('AT&T Time Warner Value Destruction Continues', 'Media consolidation strategy underperforms as streaming economics challenge legacy model.', 'Barron''s', 'Andrew Ross', '2024-01-18 08:00:00', 'https://barrons.com/at-t-time-warner', -0.68, 'negative', 'AT&T', 'Entertainment'),
('Apple Beats Integration Defines Wearables Market', 'Audio brand acquisition anchors consumer electronics ecosystem expansion.', 'MacRumors', 'Sami Patel', '2023-11-20 12:00:00', 'https://macrumors.com/apple-beats', 0.55, 'positive', 'Apple', 'Audio'),
('Oracle Sun Integration Challenges Persist', 'Enterprise software transition slower than expected with technical debt accumulation.', 'InfoWorld', 'David Flynn', ' ' '2023-09-10 09:00:00', 'https://infoworld.com/oracle-sun', -0.30, 'negative', 'Oracle', 'Technology'),
('SAP Qualtrics Experience Management Gains Enterprise Share', 'Survey and feedback platform expanding into operational analytics.', 'ZDNet', 'Stacy Howard', '2024-01-10 14:00:00', 'https://zdnet.com/sap-qualtrics', 0.60, 'positive', 'SAP', 'Survey Software'),
('Visa Plaid Deal Terminated by DOJ Antitrust Action', 'Financial data access concerns lead to abandonment of $5.3B fintech acquisition.', 'DoJ Press', 'Federal Press Office', '2021-01-12 10:00:00', 'https://doj.gov/visa-plaid', -0.88, 'negative', 'Visa', 'Fintech'),
('Snowflake RoboMQ Integration Accelerates Data Pipeline', 'iPaaS capabilities expand enterprise connectivity options.', 'Datanami', 'Bethany Clayton', '2024-02-28 11:00:00', 'https://datanami.com/snowflake-robomq', 0.70, 'positive', 'Snowflake', 'Cloud Data'),
('HP Poly Audio Video Collaboration Momentum', 'Remote work equipment demand stabilizing after post-pandemic normalization.', 'CRN', 'Kevin McCauley', ' ' '2024-01-08 09:00:00', 'https://crn.com/hp-poly', 0.35, 'positive', 'HP', 'Audio/Video'),
('Microsoft Activision Integration Revenue Synergies Exceed Targets', 'Gaming cloud infrastructure investment driving accelerated growth.', 'IGN', 'Joe Skrebels', '2024-03-05 16:00:00', 'https://ign.com/microsoft-activision', 0.72, 'positive', 'Microsoft', 'Gaming'),
('LinkedIn Microsoft Integration Surpasses Five-Year Plan', 'Professional network advertising and subscription revenue multiplication achieved.', 'LinkedIn Blog', 'Ryan Roslansky', '2023-10-15 10:00:00', 'https://linkedin.com/msft-5year', 0.80, 'positive', 'Microsoft', 'Enterprise Software'),
('UnitedHealth Change Healthcare Deal Abandoned', 'Antitrust litigation costs make transaction economically unviable.', 'Modern Healthcare', 'Tara Bannow', '2022-03-22 08:00:00', 'https://modernhealthcare.com/change-healthcare', -0.72, 'negative', 'UnitedHealth', 'Healthcare Tech'),
('Discovery Time Warner Cable Synergy Miss', 'Linear television decline accelerating post-merger integration challenges.', 'MediaPost', 'Wendell Nelson', '2023-08-10 11:00:00', 'https://mediapost.com/discovery-twc', -0.50, 'negative', 'Warner Bros', 'Entertainment'),
('Microsoft Nokia Write-Down Signals Mobile Strategy Failure', 'Device division impairment charges indicate strategic miscalculation.', 'The Register', 'Simon Sharwood', '2015-07-07 09:00:00', 'https://theregister.com/ms-nokia-writeoff', -0.65, 'negative', 'Microsoft', 'Mobile'),
('Google YouTube Monetization Evolution', 'Video platform advertising sophistication driving CPM expansion.', 'Search Engine Land', 'Ginny Mineo', '2023-12-05 10:00:00', 'https://searchengineland.com/google-youtube', 0.62, 'positive', 'Google', 'Internet Video'),
('Verizon Yahoo Email Advertising Integration Struggles', 'Legacy internet brand failing to deliver mobile-first advertising formats.', 'Digiday', 'Seb Joseph', '2024-01-12 12:00:00', 'https://digiday.com/verizon-yahoo', -0.42, 'negative', 'Verizon', 'Internet'),
('Comcast NBC Universal Content Investment Pays Off', 'Olympic and premiere content driving streaming subscriber growth.', 'Hollywood Reporter', 'Georgina Lizzi', '2024-02-01 14:00:00', 'https://hollywoodreporter.com/comcast-nbc', 0.58, 'positive', 'Comcast', 'Media')
ON CONFLICT (url) DO NOTHING;

-- =============================================================================
-- METADATA.PIPELINE_CONFIG seed
-- =============================================================================

INSERT INTO metadata.pipeline_config (pipeline_name, config_key, config_value) VALUES
('ma_ingestion', 'scraping_frequency', 'daily'),
('ma_ingestion', 'retry_attempts', '3'),
('ma_ingestion', 'batch_size', '1000'),
('news_sentiment', 'model_name', 'ProsusAI/finbert'),
('news_sentiment', 'batch_size', '32'),
('news_sentiment', 'max_articles_per_run', '500'),
('monte_carlo', 'simulations', '50000'),
('monte_carlo', 'random_seed', '42'),
('monte_carlo', 'confidence_level', '0.95'),
('recommendation', 'primary_llm', 'groq'),
('recommendation', 'fallback_llm', 'openrouter'),
('recommendation', 'temperature', '0.3'),
('recommendation', 'max_tokens', '2000'),
('scoring', 'ml_weight', '0.35'),
('scoring', 'sentiment_weight', '0.25'),
('scoring', 'simulation_weight', '0.40')
ON CONFLICT DO NOTHING;