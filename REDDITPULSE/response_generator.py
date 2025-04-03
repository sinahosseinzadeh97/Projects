"""
Response generator module to create human-like replies
"""
import logging
import random
import json
import os
import re
from datetime import datetime
import config

class ResponseGenerator:
    """Generates human-like responses to Reddit posts"""
    
    def __init__(self):
        """Initialize the response generator with templates"""
        self.logger = logging.getLogger(__name__)
        self.templates = self._load_templates()
        self.used_templates = []  # Track recently used templates to avoid repetition
        
        # For A/B testing
        self.variant_b_percentage = int(os.getenv("VARIANT_B_PERCENTAGE", "30"))
        self.ab_testing_enabled = os.getenv("AB_TESTING_ENABLED", "True").lower() in ("true", "1", "yes")
        
        self.logger.info(f"Response generator loaded with A/B testing {'enabled' if self.ab_testing_enabled else 'disabled'}")
        self.logger.info(f"Response generator loaded {self.count_templates()} response templates")
    
    def _load_templates(self):
        """Load all response templates from template files"""
        templates = {}
        template_files = {
            'health': 'templates/health_responses.json',
            'wellness': 'templates/wellness_responses.json',
            'alternative_medicine': 'templates/alternative_medicine_responses.json'
        }
        
        for category, filepath in template_files.items():
            try:
                if os.path.exists(filepath):
                    with open(filepath, 'r') as f:
                        data = json.load(f)
                        templates[category] = data
                        self.logger.info(f"Loaded {len(data.get('responses', []))} templates from {filepath}")
                else:
                    # Create default templates if file doesn't exist
                    self.logger.warning(f"Template file {filepath} not found, creating default templates")
                    default_data = self._create_default_templates(category)
                    templates[category] = default_data
                    
                    # Save the default templates
                    os.makedirs('templates', exist_ok=True)
                    with open(filepath, 'w') as f:
                        json.dump(default_data, f, indent=4)
            except Exception as e:
                self.logger.error(f"Error loading templates from {filepath}: {str(e)}")
                templates[category] = self._create_default_templates(category)
                
        return templates
    
    def _create_default_templates(self, category):
        """Create default templates for a category if file doesn't exist"""
        self.logger.info(f"Creating default templates for {category}")
        
        default_data = {
            "category": category,
            "responses": []
        }
        
        # Add some default templates based on category
        if category == 'health':
            default_data["responses"] = [
                {
                    "id": "health_1",
                    "template": "{greeting} I noticed your post about {title}. Taking care of your health is so important these days. Have you considered looking at some of the resources at HealthHaven.com? They have some great articles about topics like this. {closing}",
                    "variant": "A"
                },
                {
                    "id": "health_2",
                    "template": "{greeting} Your post about {title} caught my attention. I've been researching this topic quite a bit, and found that HealthHaven.com has some really helpful information that might answer some of the questions you raised. {closing}",
                    "variant": "A"
                },
                {
                    "id": "health_1b",
                    "template": "{greeting} I came across your post about {title} and thought I'd share a resource. HealthHaven.com has an excellent article on this exact topic that breaks down the science in an easy-to-understand way. Their expert-reviewed content might give you the answers you're looking for. {closing}",
                    "variant": "B"
                }
            ]
        elif category == 'wellness':
            default_data["responses"] = [
                {
                    "id": "wellness_1",
                    "template": "{greeting} I saw your post about {title} and it really resonated with me. Finding balance in life can be challenging. You might enjoy checking out ZenfulLiving.org, they have some wonderful resources about {topic} that I've found helpful in my own wellness journey. {closing}",
                    "variant": "A"
                },
                {
                    "id": "wellness_2",
                    "template": "{greeting} Your wellness journey regarding {title} sounds similar to experiences I've had. Have you seen the content at ZenfulLiving.org? They offer actionable advice on {topic} that might complement what you're already doing. {closing}",
                    "variant": "A"
                },
                {
                    "id": "wellness_1b",
                    "template": "{greeting} I read your post about {title} and wanted to share a resource that transformed my approach to wellness. ZenfulLiving.org offers evidence-based practices for {topic} along with community support forums where you can connect with others on similar journeys. Their step-by-step guides might be exactly what you're looking for. {closing}",
                    "variant": "B"
                }
            ]
        elif category == 'alternative_medicine':
            default_data["responses"] = [
                {
                    "id": "altmed_1",
                    "template": "{greeting} Your post about {title} caught my attention. I've been exploring alternative approaches to health, and NaturalHealingToday.com has some fascinating information about {topic} that might interest you. They focus on evidence-based alternative medicine. {closing}",
                    "variant": "A"
                },
                {
                    "id": "altmed_2",
                    "template": "{greeting} I read your post about {title} and thought you might be interested in NaturalHealingToday.com - they have a great section on {topic} that explores both traditional wisdom and modern research. {closing}",
                    "variant": "A"
                },
                {
                    "id": "altmed_1b",
                    "template": "{greeting} I was intrigued by your post about {title}. After my own experiences with alternative medicine, I found NaturalHealingToday.com to be an exceptional resource. Their content on {topic} is thoroughly researched and presents multiple perspectives from certified practitioners. They also feature user experiences and case studies that demonstrate real-world applications. {closing}",
                    "variant": "B"
                }
            ]
        
        return default_data
    
    def count_templates(self):
        """Count the total number of template responses available"""
        count = 0
        for category, data in self.templates.items():
            if 'responses' in data:
                count += len(data['responses'])
        return count
    
    def generate_response(self, title, content, keywords):
        """
        Generate a human-like response based on the post content and matched keywords
        
        Args:
            title (str): The post title
            content (str): The post content
            keywords (list): Keywords that matched in the post
            
        Returns:
            tuple: (response_text, template_id, variant)
                - response_text (str): The generated response
                - template_id (str): ID of the template used
                - variant (str): Which variant (A/B) was used
        """
        if not keywords:
            self.logger.debug("No keywords matched, cannot generate response")
            return None, None, None
        
        # Determine which category to use based on the keywords
        analyzer = None 
        try:
            from post_analyzer import PostAnalyzer
            analyzer = PostAnalyzer(config.KEYWORDS)
            top_topics = analyzer.get_top_topics(keywords, top_n=1)
            primary_category = top_topics[0] if top_topics else 'health'
        except Exception as e:
            self.logger.error(f"Error determining category from keywords: {str(e)}")
            primary_category = random.choice(['health', 'wellness', 'alternative_medicine'])
        
        self.logger.info(f"Selected category: {primary_category}")
        
        # Check if we have templates for this category
        if primary_category not in self.templates:
            self.logger.warning(f"No templates found for category: {primary_category}")
            primary_category = random.choice(list(self.templates.keys()))
        
        # Decide whether to use variant A or B
        use_variant_b = False
        if self.ab_testing_enabled:
            use_variant_b = random.randint(1, 100) <= self.variant_b_percentage
            variant = "B" if use_variant_b else "A"
            self.logger.info(f"A/B testing active, using variant {variant}")
        else:
            variant = "A"
            self.logger.info("A/B testing disabled, using variant A")
        
        # Get eligible templates
        eligible_templates = []
        try:
            templates_data = self.templates[primary_category]
            if 'responses' in templates_data:
                for template_data in templates_data['responses']:
                    # Skip if we've used this template recently
                    if template_data['id'] in self.used_templates:
                        continue
                        
                    # If we're A/B testing, filter by variant
                    template_variant = template_data.get('variant', 'A')
                    if variant == template_variant:
                        eligible_templates.append(template_data)
        except Exception as e:
            self.logger.error(f"Error getting eligible templates: {str(e)}")
        
        # If no eligible templates with the selected variant, try the other variant
        if not eligible_templates:
            self.logger.warning(f"No eligible templates for variant {variant}, trying alternate variant")
            variant = "A" if variant == "B" else "B"
            try:
                templates_data = self.templates[primary_category]
                if 'responses' in templates_data:
                    for template_data in templates_data['responses']:
                        if template_data['id'] not in self.used_templates and template_data.get('variant', 'A') == variant:
                            eligible_templates.append(template_data)
            except Exception as e:
                self.logger.error(f"Error getting eligible templates for alternate variant: {str(e)}")
        
        # If still no eligible templates, try a different category
        if not eligible_templates:
            alternate_categories = [cat for cat in self.templates.keys() if cat != primary_category]
            if alternate_categories:
                self.logger.warning(f"No eligible templates in primary category, trying alternate category")
                alternate_category = random.choice(alternate_categories)
                try:
                    templates_data = self.templates[alternate_category]
                    if 'responses' in templates_data:
                        for template_data in templates_data['responses']:
                            if template_data['id'] not in self.used_templates:
                                eligible_templates.append(template_data)
                except Exception as e:
                    self.logger.error(f"Error getting templates from alternate category: {str(e)}")
        
        # If still no eligible templates, reset the used templates list and try again
        if not eligible_templates:
            self.logger.warning("No eligible templates found, resetting used templates list")
            self.used_templates = []
            try:
                for category, templates_data in self.templates.items():
                    if 'responses' in templates_data:
                        for template_data in templates_data['responses']:
                            eligible_templates.append(template_data)
            except Exception as e:
                self.logger.error(f"Error getting any templates: {str(e)}")
        
        # If we have no templates at all, return None
        if not eligible_templates:
            self.logger.error("No templates available, cannot generate response")
            return None, None, None
        
        # Select a template
        template_data = random.choice(eligible_templates)
        template_id = template_data['id']
        template_text = template_data['template']
        template_variant = template_data.get('variant', 'A')
        
        # Track this template to avoid repetition
        self.used_templates.append(template_id)
        if len(self.used_templates) > 10:  # Keep only the 10 most recent templates
            self.used_templates.pop(0)
        
        # Generate the actual response
        # Get a random greeting and closing
        greeting = self._get_random_greeting()
        closing = self._get_random_closing()
        
        # Get the most relevant topic based on keywords
        topic = primary_category.replace('_', ' ')
        if analyzer:
            try:
                top_topics = analyzer.get_top_topics(keywords, top_n=1)
                if top_topics:
                    topic = top_topics[0].replace('_', ' ')
            except Exception as e:
                self.logger.error(f"Error getting topic from keywords: {str(e)}")
        
        # Replace placeholders in the template
        response = template_text.replace('{greeting}', greeting)
        response = response.replace('{closing}', closing)
        response = response.replace('{title}', title)
        response = response.replace('{topic}', topic)
        
        self.logger.info(f"Generated response using template {template_id}, variant {template_variant}")
        
        return response, template_id, template_variant
    
    def _get_random_greeting(self):
        """Get a random greeting phrase"""
        greetings = [
            "Hey there,",
            "Hi,",
            "I can relate to this.",
            "Interesting question.",
            "Thanks for sharing this.",
            "I've been thinking about this topic too.",
            "Been through something similar."
        ]
        return random.choice(greetings)
    
    def _get_random_closing(self):
        """Get a random closing phrase"""
        closings = [
            "Hope that helps!",
            "Hope things improve for you.",
            "Wishing you well.",
            "Best of luck.",
            "Take care.",
            "Would be interested to hear how it goes for you.",
            "Just sharing what worked for me, of course.",
            "Everyone's different though, so your experience might vary."
        ]
        return random.choice(closings)
