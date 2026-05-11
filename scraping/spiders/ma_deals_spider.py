import scrapy
from datetime import datetime
import json
import hashlib


class MaDealsSpider(scrapy.Spider):
    name = 'ma_deals'
    allowed_domains = [
        'mergers.com',
        'cap Iqbal.com',
        'dealogic.com',
        'bloomberg.com',
        'wsj.com',
        'reuters.com',
    ]
    start_urls = [
        'https://www.mergers.com/transactions',
    ]

    custom_settings = {
        'CONCURRENT_REQUESTS': 1,
        'DOWNLOAD_DELAY': 1,
        'RANDOMIZE_DOWNLOAD_DELAY': True,
        'USER_AGENT': 'DealSenseBot/1.0 (+https://dealsense.ai)',
        'ROBOTSTXT_OBEY': True,
        'HTTPCACHE_ENABLED': True,
        'HTTPCACHE_EXPIRATION_SECS': 86400,
    }

    def parse(self, response):
        """Parse M&A deal listings."""
        deals = response.css('div.deal-card, table.deals-table tr.deal-row')

        for deal in deals:
            item = self.parse_deal_card(deal)
            if item:
                yield item

        next_page = response.css('a.next::attr(href)').get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_deal_card(self, selector):
        """Extract deal fields from a card or table row."""
        try:
            acquirer = selector.css('.acquirer-name::text, td.acquirer::text').get()
            target = selector.css('.target-name::text, td.target::text').get()
            deal_value = selector.css('.deal-value::text, td.value::text').get()
            date_str = selector.css('.date::text, td.date::text').get()
            industry = selector.css('.industry::text, td.industry::text').get()

            if not acquirer or not target:
                return None

            deal_value_clean = self.parse_value(deal_value)
            date_clean = self.parse_date(date_str)

            item = {
                'acquirer': self.clean_text(acquirer),
                'target': self.clean_text(target),
                'deal_value_usd': deal_value_clean,
                'industry': self.clean_text(industry),
                'announcement_date': date_clean,
                'deal_status': 'completed',
                'source_url': '',
                'scraped_at': datetime.utcnow().isoformat(),
                'raw_hash': hashlib.md5(f"{acquirer}{target}{date_clean}".encode()).hexdigest(),
            }

            self.logger.info(f"Parsed deal: {item['acquirer']} -> {item['target']} (${deal_value_clean:,.0f})")
            return item

        except Exception as e:
            self.logger.error(f"Failed to parse deal: {e}")
            return None

    def parse_value(self, value_str):
        """Convert deal value string to USD integer."""
        if not value_str:
            return 0

        value_str = value_str.upper().strip()
        multiplier = 1

        if 'B' in value_str:
            multiplier = 1_000_000_000
            value_str = value_str.replace('B', '')
        elif 'M' in value_str:
            multiplier = 1_000_000
            value_str = value_str.replace('M', '')
        elif 'K' in value_str:
            multiplier = 1_000
            value_str = value_str.replace('K', '')

        try:
            value_str = ''.join(c for c in value_str if c.isdigit() or c == '.')
            return int(float(value_str) * multiplier)
        except (ValueError, TypeError):
            return 0

    def parse_date(self, date_str):
        """Parse various date formats to ISO date string."""
        if not date_str:
            return None

        formats = [
            '%Y-%m-%d', '%Y/%m/%d', '%d-%b-%Y', '%d/%m/%Y',
            '%B %d, %Y', '%b %d, %Y', '%m/%d/%Y', '%d.%m.%Y',
        ]

        date_str = date_str.strip()
        for fmt in formats:
            try:
                dt = datetime.strptime(date_str, fmt)
                return dt.strftime('%Y-%m-%d')
            except ValueError:
                continue

        return None

    def clean_text(self, text):
        """Clean and normalize text."""
        if not text:
            return ''
        import re
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    def start_requests(self):
        """Override to support multiple data sources."""
        urls = [
            'https://www.mergers.com/large-deals',
            'https://www.mergers.com/tech-sector',
            'https://www.mergers.com/2024-deals',
        ]
        for url in urls:
            yield scrapy.Request(url, callback=self.parse)

    def closed(self, reason):
        """Called when spider is closed. Log summary."""
        self.logger.info(f"Spider closed: {reason}")
        self.logger.info(f"Scraped {len(self.items)} deals")