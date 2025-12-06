"""
AI Agent Service using DeepSeek API
Handles conversational AI, natural language queries, and intelligent recommendations
"""
import json
import re
import httpx
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from loguru import logger

from app.core.config import settings


class AIAgentService:
    """AI Agent service for natural language processing and intelligent recommendations"""
    
    def __init__(self):
        """Initialize AI Agent service"""
        self.api_key = settings.DEEPSEEK_API_KEY
        self.base_url = settings.DEEPSEEK_BASE_URL
        self.model = settings.DEEPSEEK_MODEL
        self.client = httpx.AsyncClient(timeout=60.0)
        
        # Log configuration (without exposing API key)
        if self.api_key and self.api_key.strip():
            masked_key = '*' * (len(self.api_key) - 4) + self.api_key[-4:] if len(self.api_key) > 4 else '***'
            logger.info(f"DeepSeek AI Agent initialized - Model: {self.model}, Base URL: {self.base_url}, API Key: {masked_key}")
        else:
            logger.warning("DeepSeek API key is not configured. AI features will not work. Please set DEEPSEEK_API_KEY in .env file.")
        
    async def __aenter__(self):
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
    
    async def _call_deepseek(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> str:
        """
        Call DeepSeek API
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum tokens to generate
            
        Returns:
            Generated response text
        """
        # Validate API key
        if not self.api_key or self.api_key.strip() == "":
            error_msg = "DeepSeek API key is not configured. Please set DEEPSEEK_API_KEY in your .env file."
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        try:
            url = f"{self.base_url}/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": self.model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens
            }
            
            logger.debug(f"Calling DeepSeek API: {url} with model {self.model}")
            
            response = await self.client.post(url, headers=headers, json=payload, timeout=60.0)
            
            # Check status code before parsing
            if response.status_code != 200:
                error_text = response.text[:500] if response.text else "No error details"
                error_msg = f"DeepSeek API returned status {response.status_code}: {error_text}"
                logger.error(error_msg)
                
                # Try to parse error response for better error message
                try:
                    error_json = response.json()
                    if "error" in error_json:
                        error_detail = error_json["error"].get("message", error_text)
                        error_code = error_json["error"].get("code", "unknown")
                        raise Exception(f"DeepSeek API error ({error_code}): {error_detail}")
                except Exception as parse_error:
                    # If we already raised an exception with better details, re-raise it
                    if "DeepSeek API error" in str(parse_error):
                        raise
                    # Otherwise, raise the original error message
                    pass
                
                raise Exception(error_msg)
            
            result = response.json()
            
            # Validate response structure
            if "choices" not in result:
                error_msg = "Invalid response from DeepSeek API: Missing 'choices' field"
                logger.error(f"{error_msg}. Response keys: {list(result.keys())}")
                raise ValueError(error_msg)
            
            if len(result["choices"]) == 0:
                error_msg = "Invalid response from DeepSeek API: Empty choices array"
                logger.error(f"{error_msg}. Response: {result}")
                raise ValueError(error_msg)
            
            if "message" not in result["choices"][0]:
                error_msg = "Invalid response from DeepSeek API: Missing 'message' in choice"
                logger.error(f"{error_msg}. Choice structure: {result['choices'][0]}")
                raise ValueError(error_msg)
            
            if "content" not in result["choices"][0]["message"]:
                error_msg = "Invalid response from DeepSeek API: Missing 'content' in message"
                logger.error(f"{error_msg}. Message structure: {result['choices'][0]['message']}")
                raise ValueError(error_msg)
            
            content = result["choices"][0]["message"]["content"]
            if not content or not isinstance(content, str):
                error_msg = f"Invalid response from DeepSeek API: Content is not a string (type: {type(content)})"
                logger.error(error_msg)
                raise ValueError(error_msg)
            
            logger.debug(f"Successfully received response from DeepSeek API ({len(content)} characters)")
            return content
            
        except httpx.TimeoutException as e:
            error_msg = f"DeepSeek API request timed out after 60 seconds: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)
        except httpx.HTTPStatusError as e:
            # Try to extract error details from response
            error_text = "No error details"
            status_code = e.response.status_code if hasattr(e, 'response') else "unknown"
            
            try:
                if hasattr(e, 'response') and e.response:
                    if e.response.text:
                        error_text = e.response.text[:500]
                        # Try to parse as JSON
                        try:
                            error_json = e.response.json()
                            if "error" in error_json:
                                error_detail = error_json["error"]
                                error_text = error_detail.get("message", error_detail.get("type", error_text))
                                error_code = error_detail.get("code", "")
                                if error_code:
                                    error_text = f"{error_code}: {error_text}"
                        except:
                            pass
            except Exception as parse_err:
                error_text = f"Error parsing response: {str(parse_err)}"
            
            error_msg = f"DeepSeek API HTTP error {status_code}: {error_text}"
            logger.error(error_msg)
            logger.debug(f"Full error response: {e.response.text if hasattr(e, 'response') and e.response else 'N/A'}")
            raise Exception(error_msg)
        except httpx.RequestError as e:
            error_msg = f"DeepSeek API request error: {type(e).__name__}: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)
        except httpx.HTTPError as e:
            error_msg = f"DeepSeek API HTTP error: {type(e).__name__}: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)
        except ValueError as e:
            # Re-raise ValueError as-is (API key validation, response validation)
            raise
        except Exception as e:
            error_msg = f"Unexpected error calling DeepSeek API: {type(e).__name__}: {str(e)}"
            logger.error(error_msg, exc_info=True)
            raise Exception(error_msg)
    
    async def process_natural_language_query(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None,
        app_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process natural language query about flights/cargo
        
        Args:
            query: User's natural language query
            context: Optional context (flight data, etc.)
            app_context: Full application context
            
        Returns:
            Dict with structured query information
        """
        system_prompt = """You are an AI assistant for a cargo analytics system. 
You have FULL ACCESS to the database and can understand complex queries.

Extract the following information from queries:
- Query type: 'search_flights', 'get_capacity', 'get_risk', 'get_recommendations', 
  'explain', 'get_route_stats', 'get_airport_stats', 'get_flight_details', 'other'
- Flight filters: flight_number, origin, destination, date_range, status, flight_type
- Risk level: 'high', 'medium', 'low', or None
- Days before flight: number or None
- Other parameters as needed

Available database tables: flights, aircraft, airports, airlines, weather_data, 
airport_traffic, flight_delay_predictions, cargo_predictions, passenger_traffic_predictions

Return ONLY valid JSON with this structure:
{
    "query_type": "search_flights",
    "filters": {
        "risk_level": "high",
        "date_range": {"start": "2024-12-01", "end": "2024-12-07"},
        "origin": "KUL",
        "destination": null,
        "flight_status": null,
        "flight_type": null
    },
    "days_before_flight": 7,
    "intent": "User wants to find flights with high overbooking risk next week",
    "needs_data": true,
    "data_queries": ["query_flights", "get_route_stats"]
}"""

        context_info = ""
        if app_context:
            stats = app_context.get("data_statistics", {})
            context_info = f"\nDatabase has {stats.get('total_flights', 0)} flights, {stats.get('total_airports', 0)} airports."
        
        user_prompt = f"""User query: "{query}"

Current date: {datetime.now().strftime('%Y-%m-%d')}
{context_info}

Context: {json.dumps(context) if context else 'None'}

Extract the query intent and parameters. Return ONLY valid JSON."""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        try:
            response = await self._call_deepseek(messages, temperature=0.3, max_tokens=800)
            # Parse JSON from response
            response = response.strip()
            if response.startswith("```json"):
                response = response[7:]
            if response.startswith("```"):
                response = response[3:]
            if response.endswith("```"):
                response = response[:-3]
            response = response.strip()
            
            parsed = json.loads(response)
            return parsed
        except json.JSONDecodeError:
            logger.warning(f"Failed to parse AI response as JSON: {response}")
            # Fallback: return basic structure
            return {
                "query_type": "other",
                "filters": {},
                "intent": query,
                "needs_data": True
            }
    
    async def generate_insights(
        self,
        prediction_data: Dict[str, Any],
        flight_data: Dict[str, Any]
    ) -> str:
        """
        Generate natural language insights from prediction data
        
        Args:
            prediction_data: ML prediction results
            flight_data: Flight information
            
        Returns:
            Natural language explanation
        """
        system_prompt = """You are a cargo analytics expert. Explain flight cargo capacity predictions 
in clear, actionable language. Focus on:
- What the numbers mean
- Why the risk level is what it is
- What actions the user should consider
- Key constraints (weight vs volume)

Be concise (2-3 sentences) but informative."""

        user_prompt = f"""Flight: {flight_data.get('flight_number', 'Unknown')}
Route: {flight_data.get('origin', '')} → {flight_data.get('destination', '')}
Date: {flight_data.get('scheduled_departure', 'Unknown')}

Prediction Data:
- Available Weight: {prediction_data.get('available_weight_kg', 0) / 1000:.2f} tonnes
- Available Volume: {prediction_data.get('available_volume_m3', 0):.2f} m³
- Constraining Factor: {prediction_data.get('constraining_factor', 'unknown')}
- Overbooking Risk: {prediction_data.get('overbooking_risk', 'unknown')}
- Days Before Flight: {prediction_data.get('days_before_flight', 0)}

Baggage Prediction:
- Predicted Baggage Weight: {prediction_data.get('predicted_baggage_weight_kg', 0) / 1000:.2f} tonnes
- Predicted Baggage Volume: {prediction_data.get('predicted_baggage_volume_m3', 0):.2f} m³

Explain this prediction in natural language."""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        response = await self._call_deepseek(messages, temperature=0.7, max_tokens=300)
        
        # Filter out code blocks and SQL commands
        filtered_response = self._filter_code_and_sql(response)
        
        return filtered_response
    
    async def generate_cargo_recommendations(
        self,
        available_weight_kg: float,
        available_volume_m3: float,
        constraining_factor: str,
        route_info: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate intelligent cargo mix recommendations
        
        Args:
            available_weight_kg: Available weight capacity
            available_volume_m3: Available volume capacity
            constraining_factor: 'weight' or 'volume'
            route_info: Optional route information
            
        Returns:
            Dict with recommendations
        """
        system_prompt = """You are a cargo optimization expert. Given available capacity, 
recommend optimal cargo mix to maximize revenue.

Consider:
- If weight-constrained: Recommend dense, high-value cargo (electronics, machinery)
- If volume-constrained: Recommend lightweight, high-value cargo (textiles, pharmaceuticals)
- Typical cargo densities and values
- Route-specific preferences

Return JSON with:
{
    "recommended_cargo_mix": [
        {"type": "Electronics", "weight_kg": 2000, "volume_m3": 5, "priority": "high", "reason": "..."},
        ...
    ],
    "total_weight_kg": 0,
    "total_volume_m3": 0,
    "utilization_percentage": 0,
    "revenue_estimate": "high/medium/low",
    "reasoning": "Explanation of recommendations"
}"""

        user_prompt = f"""Available Capacity:
- Weight: {available_weight_kg / 1000:.2f} tonnes
- Volume: {available_volume_m3:.2f} m³
- Constraining Factor: {constraining_factor}

Route: {route_info.get('origin', '')} → {route_info.get('destination', '')} if route_info else 'Unknown'

Recommend optimal cargo mix. Return ONLY valid JSON."""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        try:
            response = await self._call_deepseek(messages, temperature=0.5, max_tokens=1000)
            # Parse JSON
            response = response.strip()
            if response.startswith("```json"):
                response = response[7:]
            if response.startswith("```"):
                response = response[3:]
            if response.endswith("```"):
                response = response[:-3]
            response = response.strip()
            
            parsed = json.loads(response)
            return parsed
        except json.JSONDecodeError:
            logger.warning("Failed to parse cargo recommendations")
            return {
                "recommended_cargo_mix": [],
                "reasoning": "Unable to generate recommendations at this time"
            }
    
    async def generate_alert_explanation(
        self,
        alert_type: str,
        flight_data: Dict[str, Any],
        metrics: Dict[str, Any]
    ) -> str:
        """
        Generate explanation for proactive alerts
        
        Args:
            alert_type: Type of alert ('high_risk', 'low_capacity', 'opportunity')
            flight_data: Flight information
            metrics: Alert metrics
            
        Returns:
            Natural language alert message
        """
        system_prompt = """You are an alert system for cargo operations. Generate clear, 
actionable alert messages. Be concise but informative."""

        user_prompt = f"""Alert Type: {alert_type}
Flight: {flight_data.get('flight_number', 'Unknown')}
Route: {flight_data.get('origin', '')} → {flight_data.get('destination', '')}

Metrics: {json.dumps(metrics, indent=2)}

Generate a clear alert message explaining the issue and recommended action."""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        response = await self._call_deepseek(messages, temperature=0.6, max_tokens=200)
        
        # Filter out code blocks and SQL commands
        filtered_response = self._filter_code_and_sql(response)
        
        return filtered_response
    
    async def chat_conversation(
        self,
        user_message: str,
        conversation_history: List[Dict[str, str]],
        context: Optional[Dict[str, Any]] = None,
        app_context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Handle conversational chat with full application context
        
        Args:
            user_message: User's message
            conversation_history: Previous messages in conversation
            context: Current context (selected flight, etc.)
            app_context: Full application context from AIContextProvider
            
        Returns:
            AI response
        """
        system_prompt = """You are an expert AI assistant for a cargo analytics system. 
You have FULL ACCESS to all application data, database, and services.

## Your Capabilities:

### Database Access:
- Query flights by number, route, date, status
- Get detailed flight information
- Access aircraft, airport, airline data
- View historical weather and traffic data
- Access ML predictions and model information

### Services Available:
- ML Service: Predict cargo capacity, delays, demand, traffic
- Flight Tracking: Get aircraft info, routes, real-time status
- Cargo Optimization: Generate optimal cargo mix recommendations
- Alert Service: Check for capacity issues and risks

### What You Can Do:
1. **Answer Questions**: About any flight, route, aircraft, or airport
2. **Analyze Data**: Compare routes, identify patterns, explain trends
3. **Make Predictions**: Use ML services to predict capacity, delays, demand
4. **Provide Recommendations**: Cargo optimization, route selection, risk mitigation
5. **Explain Insights**: Interpret predictions, explain risk levels, clarify metrics
6. **Query Database**: Search flights, get statistics, analyze historical data

### Important Response Guidelines:
- You have access to ALL data in the system
- You can query the database through the context provider
- You can call any service or API endpoint
- Be specific and accurate in your responses
- Use actual data from the system when available
- **NEVER include SQL queries, code blocks, or technical implementation details in your responses**
- **NEVER show database commands, API calls, or system commands**
- **ONLY provide natural language explanations and insights**
- **Focus on answering the user's question in plain, conversational language**

Be helpful, professional, and use the comprehensive context provided to give accurate answers in natural language only."""

        messages = [{"role": "system", "content": system_prompt}]
        
        # Add comprehensive application context
        if app_context:
            context_summary = self._summarize_context(app_context)
            messages.append({
                "role": "system",
                "content": f"## Application Context:\n{context_summary}\n\nUse this information to answer user questions accurately."
            })
        
        # Add conversation history
        messages.extend(conversation_history)
        
        # Add current context if available
        if context:
            context_msg = f"\n[Current User Context: {json.dumps(context, indent=2)}]"
            if messages[-1]["role"] == "user":
                messages[-1]["content"] += context_msg
            else:
                messages.append({"role": "system", "content": f"Current Context: {context_msg}"})
        
        # Add current user message
        messages.append({"role": "user", "content": user_message})
        
        response = await self._call_deepseek(messages, temperature=0.7, max_tokens=2500)
        
        # Filter out code blocks and SQL commands
        filtered_response = self._filter_code_and_sql(response)
        
        return filtered_response
    
    def _filter_code_and_sql(self, text: str) -> str:
        """
        Remove code blocks, SQL commands, and technical implementation details from AI responses
        
        Args:
            text: Raw AI response text
            
        Returns:
            Filtered text without code blocks or SQL
        """
        if not text:
            return text
        
        # Remove code blocks (```code``` or ```language\ncode\n```)
        text = re.sub(r'```[\s\S]*?```', '', text)
        
        # Remove inline code that looks like SQL or commands
        # Keep simple inline code like `variable_name` but remove SQL/commands
        lines = text.split('\n')
        filtered_lines = []
        
        for line in lines:
            # Skip lines that look like SQL commands
            sql_keywords = [
                r'^\s*(SELECT|INSERT|UPDATE|DELETE|CREATE|DROP|ALTER|GRANT|REVOKE)',
                r'^\s*(FROM|WHERE|JOIN|INNER|OUTER|LEFT|RIGHT|ON|GROUP BY|ORDER BY|HAVING)',
                r'^\s*(BEGIN|COMMIT|ROLLBACK|TRANSACTION)',
                r'^\s*--.*',  # SQL comments
                r'^\s*/\*.*\*/',  # SQL block comments
            ]
            
            is_sql = any(re.match(pattern, line, re.IGNORECASE) for pattern in sql_keywords)
            
            # Skip lines that look like command-line commands
            is_command = re.match(r'^\s*\$|^\s*#|^\s*>\s*\w+', line)
            
            # Skip lines that look like Python/JavaScript code blocks
            is_code_block = (
                re.match(r'^\s*(def|class|import|from|const|let|var|function|async|await)\s+', line, re.IGNORECASE) or
                re.match(r'^\s*(if|for|while|try|except|catch|return|yield)\s+', line, re.IGNORECASE)
            )
            
            # Skip lines that are just code-like patterns
            if is_sql or is_command or is_code_block:
                continue
            
            # Remove inline code blocks that contain SQL keywords
            line = re.sub(r'`[^`]*\b(SELECT|INSERT|UPDATE|DELETE|FROM|WHERE|JOIN|CREATE|DROP)\b[^`]*`', '', line, flags=re.IGNORECASE)
            
            # Remove command-like patterns in text
            line = re.sub(r'\$\s*\w+.*', '', line)  # Remove $ command patterns
            line = re.sub(r'#\s*\w+.*', '', line)  # Remove # command patterns
            
            filtered_lines.append(line)
        
        text = '\n'.join(filtered_lines)
        
        # Clean up multiple blank lines
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        # Remove any remaining code-like patterns
        text = re.sub(r'```.*?```', '', text, flags=re.DOTALL)
        
        return text.strip()
    
    def _summarize_context(self, app_context: Dict[str, Any]) -> str:
        """Summarize application context for AI"""
        summary = []
        
        # Application info
        app_info = app_context.get("application", {})
        summary.append(f"Application: {app_info.get('application_name', 'Cargo Analytics')}")
        summary.append(f"Version: {app_info.get('version', '1.0.0')}")
        
        # Database statistics
        stats = app_context.get("data_statistics", {})
        if stats:
            summary.append(f"\nDatabase Statistics:")
            summary.append(f"- Total Flights: {stats.get('total_flights', 0)}")
            summary.append(f"- Total Aircraft: {stats.get('total_aircraft', 0)}")
            summary.append(f"- Total Airports: {stats.get('total_airports', 0)}")
            summary.append(f"- Total Airlines: {stats.get('total_airlines', 0)}")
        
        # Available services
        services = app_context.get("services", {})
        if services:
            summary.append(f"\nAvailable Services:")
            for service_name, service_info in services.items():
                summary.append(f"- {service_name}: {service_info.get('description', '')}")
                capabilities = service_info.get('capabilities', [])
                if capabilities:
                    summary.append(f"  Capabilities: {', '.join(capabilities[:3])}...")
        
        # Database tables
        schema = app_context.get("database_schema", {})
        if schema:
            summary.append(f"\nDatabase Tables ({len(schema)}):")
            for table_name in list(schema.keys())[:5]:
                table_info = schema[table_name]
                summary.append(f"- {table_name}: {table_info.get('description', '')}")
            if len(schema) > 5:
                summary.append(f"  ... and {len(schema) - 5} more tables")
        
        return "\n".join(summary)
    
    async def process_feedback(
        self,
        feedback: str,
        prediction_id: Optional[str] = None,
        correction_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process user feedback to improve predictions
        
        Args:
            feedback: User feedback text
            prediction_id: ID of prediction being feedback on
            correction_data: Corrected values if any
            
        Returns:
            Dict with extracted feedback insights
        """
        system_prompt = """Extract insights from user feedback about cargo predictions.
Identify:
- What was wrong (if anything)
- What was correct
- Suggestions for improvement
- User preferences

Return JSON with:
{
    "sentiment": "positive/negative/neutral",
    "issues": ["issue1", "issue2"],
    "corrections": {"field": "value"},
    "preferences": {"preference": "value"},
    "suggestions": ["suggestion1", "suggestion2"]
}"""

        user_prompt = f"""User Feedback: "{feedback}"

Prediction ID: {prediction_id or 'N/A'}
Correction Data: {json.dumps(correction_data) if correction_data else 'None'}

Extract insights. Return ONLY valid JSON."""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        try:
            response = await self._call_deepseek(messages, temperature=0.3, max_tokens=500)
            response = response.strip()
            if response.startswith("```json"):
                response = response[7:]
            if response.startswith("```"):
                response = response[3:]
            if response.endswith("```"):
                response = response[:-3]
            response = response.strip()
            
            parsed = json.loads(response)
            return parsed
        except json.JSONDecodeError:
            return {
                "sentiment": "neutral",
                "issues": [],
                "corrections": {},
                "preferences": {},
                "suggestions": []
            }
