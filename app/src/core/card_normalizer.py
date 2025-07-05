import re
from collections import defaultdict
from unidecode import unidecode
import json
from abc import ABC, abstractmethod

def jaro_winkler_similarity(s1, s2, prefix_weight=0.1):
    """
    Implementación de Jaro-Winkler similarity
    prefix_weight: peso del prefijo común (0.1 es estándar)
    """
    if s1 == s2:
        return 1.0
    
    if not s1 or not s2:
        return 0.0
    
    # Calcular Jaro similarity
    def jaro_similarity(str1, str2):
        if str1 == str2:
            return 1.0
        
        len1, len2 = len(str1), len(str2)
        if len1 == 0 or len2 == 0:
            return 0.0
        
        # Distancia máxima para considerar una coincidencia
        match_distance = max(len1, len2) // 2 - 1
        match_distance = max(0, match_distance)
        
        # Arrays para marcar coincidencias
        str1_matches = [False] * len1
        str2_matches = [False] * len2
        
        matches = 0
        transpositions = 0
        
        # Encontrar coincidencias
        for i in range(len1):
            start = max(0, i - match_distance)
            end = min(i + match_distance + 1, len2)
            
            for j in range(start, end):
                if str2_matches[j] or str1[i] != str2[j]:
                    continue
                str1_matches[i] = True
                str2_matches[j] = True
                matches += 1
                break
        
        if matches == 0:
            return 0.0
        
        # Contar transposiciones
        k = 0
        for i in range(len1):
            if not str1_matches[i]:
                continue
            while not str2_matches[k]:
                k += 1
            if str1[i] != str2[k]:
                transpositions += 1
            k += 1
        
        jaro = (matches / len1 + matches / len2 + 
                (matches - transpositions / 2) / matches) / 3.0
        
        return jaro
    
    jaro_sim = jaro_similarity(s1, s2)
    
    # Si Jaro < 0.7, no aplicar bonus de prefijo
    if jaro_sim < 0.7:
        return jaro_sim
    
    # Calcular prefijo común (máximo 4 caracteres)
    prefix_length = 0
    for i in range(min(len(s1), len(s2), 4)):
        if s1[i] == s2[i]:
            prefix_length += 1
        else:
            break
    
    # Aplicar bonus de Winkler
    return jaro_sim + (prefix_length * prefix_weight * (1 - jaro_sim))

class BaseTCGMatcher(ABC):
    """Clase base para matchers de TCG"""
    
    def __init__(self):
        self.grouped_cards = defaultdict(list)
        
    def normalize_text(self, text):
        """Normaliza el texto para comparación"""
        if not text:
            return ""
            
        # Convertir a minúsculas y remover acentos
        text = unidecode(text.lower())
        
        # Remover caracteres especiales excepto espacios y guiones
        text = re.sub(r'[^\w\s\-]', ' ', text)
        
        # Normalizar espacios múltiples
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    @abstractmethod
    def extract_card_group(self, card_name):
        """Extrae el grupo principal de la carta (debe ser implementado por cada TCG)"""
        pass
    
    @abstractmethod
    def preprocess_card_name(self, name):
        """Preprocesamiento específico del TCG"""
        pass
    
    def group_cards(self, card_list):
        """Agrupa las cartas por su grupo principal"""
        self.grouped_cards.clear()
        ungrouped_cards = []
        
        for card in card_list:
            group_name = self.extract_card_group(card)
            
            if group_name:
                self.grouped_cards[group_name].append(card)
            else:
                ungrouped_cards.append(card)
        
        # Agregar cartas no agrupadas a un grupo especial
        if ungrouped_cards:
            self.grouped_cards['_ungrouped'].extend(ungrouped_cards)
        
        return dict(self.grouped_cards)
    
    def find_matches_in_group(self, query_card, candidate_group, threshold=0.85):
        """Encuentra matches dentro de un grupo específico usando Jaro-Winkler"""
        query_processed = self.preprocess_card_name(query_card)
        
        matches = []
        
        for candidate in candidate_group:
            candidate_processed = self.preprocess_card_name(candidate)
            
            # Múltiples estrategias con Jaro-Winkler
            scores = {}
            
            # 1. Comparación directa completa
            scores['full_match'] = jaro_winkler_similarity(query_processed, candidate_processed)
            
            # 2. Comparación por tokens (palabras)
            query_tokens = query_processed.split()
            candidate_tokens = candidate_processed.split()
            
            # Token matching: mejor score entre todos los pares de tokens
            token_scores = []
            for q_token in query_tokens:
                best_token_score = 0
                for c_token in candidate_tokens:
                    token_score = jaro_winkler_similarity(q_token, c_token)
                    best_token_score = max(best_token_score, token_score)
                token_scores.append(best_token_score)
            
            scores['token_match'] = sum(token_scores) / len(token_scores) if token_scores else 0
            
            # 3. Ordenamiento de tokens (para manejar orden diferente)
            query_sorted = ' '.join(sorted(query_tokens))
            candidate_sorted = ' '.join(sorted(candidate_tokens))
            scores['sorted_match'] = jaro_winkler_similarity(query_sorted, candidate_sorted)
            
            # 4. Match de prefijo (muy importante para nombres)
            if query_processed and candidate_processed:
                if query_processed[0] == candidate_processed[0]:
                    scores['prefix_bonus'] = 0.1
                else:
                    scores['prefix_bonus'] = 0
            
            # Calcular score final (combinación ponderada)
            weights = {
                'full_match': 0.4,
                'token_match': 0.3, 
                'sorted_match': 0.2,
                'prefix_bonus': 0.1
            }
            
            final_score = sum(scores[key] * weights[key] for key in weights)
            
            if final_score >= threshold:
                matches.append({
                    'card': candidate,
                    'score': final_score * 100,
                    'scores_detail': {k: v * 100 for k, v in scores.items()}
                })
        
        matches.sort(key=lambda x: x['score'], reverse=True)
        return matches
    
    def batch_match_cards(self, query_cards, candidate_cards, threshold=0.85):
        """Hace matching de múltiples cartas de forma eficiente"""
        grouped_candidates = self.group_cards(candidate_cards)
        results = {}
        
        for query_card in query_cards:
            query_group = self.extract_card_group(query_card)
            
            if query_group and query_group in grouped_candidates:
                matches = self.find_matches_in_group(
                    query_card,
                    grouped_candidates[query_group],
                    threshold
                )
            else:
                matches = []
                search_groups = ['_ungrouped']
                
                for group_name, cards in grouped_candidates.items():
                    if len(cards) <= 20 and group_name != '_ungrouped':
                        search_groups.append(group_name)
                
                for group_name in search_groups:
                    if group_name in grouped_candidates:
                        group_matches = self.find_matches_in_group(
                            query_card,
                            grouped_candidates[group_name],
                            threshold
                        )
                        matches.extend(group_matches)
            
            if matches:
                matches.sort(key=lambda x: x['score'], reverse=True)
                results[query_card] = matches[0]
            else:
                results[query_card] = None
        
        return results

class PokemonCardMatcher(BaseTCGMatcher):
    """Matcher específico para cartas Pokémon"""
    
    def __init__(self):
        super().__init__()
        self.pokemon_names = [
            'pikachu', 'charizard', 'blastoise', 'venusaur', 'mewtwo', 'mew',
            'lugia', 'ho-oh', 'rayquaza', 'kyogre', 'groudon', 'dialga', 'palkia',
            'giratina', 'arceus', 'reshiram', 'zekrom', 'kyurem', 'xerneas', 'yveltal',
            'zygarde', 'solgaleo', 'lunala', 'necrozma', 'zacian', 'zamazenta',
            'eternatus', 'calyrex', 'koraidon', 'miraidon', 'alakazam', 'machamp',
            'gengar', 'dragonite', 'tyranitar', 'salamence', 'metagross', 'garchomp',
            'lucario', 'zoroark', 'greninja', 'talonflame', 'decidueye', 'incineroar',
            'primarina', 'toxapex', 'mimikyu', 'dragapult', 'corviknight', 'grimmsnarl'
        ]
        
        self.pokemon_variations = {
            'charizard': ['charizard', 'lizardon', 'dracaufeu'],
            'pikachu': ['pikachu', 'pikachú', 'pikachù'],
            'mewtwo': ['mewtwo', 'mew-two', 'mew two'],
            'ho-oh': ['ho-oh', 'ho oh', 'hooh'],
        }
        
        self.card_types = [
            'ex', 'gx', 'v', 'vmax', 'vstar', 'tag team', 'break', 'prime',
            'lv.x', 'mega', 'prism star', 'radiant', 'shining', 'crystal',
            'delta species', 'holo', 'reverse', 'full art', 'secret', 'rainbow'
        ]
    
    def extract_card_group(self, card_name):
        """Extrae el nombre del Pokémon de la carta"""
        normalized = self.normalize_text(card_name)
        
        # Primero busca variaciones específicas
        for pokemon, variations in self.pokemon_variations.items():
            for variation in variations:
                if variation in normalized:
                    return pokemon
        
        # Luego busca nombres directos
        best_match = None
        best_score = 0
        
        for pokemon in self.pokemon_names:
            words = normalized.split()
            partial_score = 0
            for word in words:
                word_score = jaro_winkler_similarity(pokemon, word)
                partial_score = max(partial_score, word_score)
            
            score = partial_score * 100
            if score > best_score and score >= 80:
                best_score = score
                best_match = pokemon
        
        return best_match
    
    def preprocess_card_name(self, name):
        """Preprocesamiento específico para cartas Pokémon"""
        name = self.normalize_text(name)
        
        # Normalizar tipos de carta
        for card_type in self.card_types:
            pattern = rf'\b{re.escape(card_type)}\b'
            name = re.sub(pattern, card_type.upper(), name, flags=re.IGNORECASE)
        
        # Remover números de colección
        name = re.sub(r'\b\d{1,3}/\d{1,3}\b', '', name)
        name = re.sub(r'#\d+', '', name)
        name = re.sub(r'\(\d+\)', '', name)
        
        return re.sub(r'\s+', ' ', name).strip()

class YugiohCardMatcher(BaseTCGMatcher):
    """Matcher específico para cartas Yu-Gi-Oh!"""
    
    def __init__(self):
        super().__init__()
        # Arquetipos populares de Yu-Gi-Oh!
        self.archetypes = [
            'blue-eyes', 'dark magician', 'red-eyes', 'elemental hero', 'blackwing',
            'lightsworn', 'six samurai', 'dragon ruler', 'burning abyss', 'shaddoll',
            'qliphort', 'nekroz', 'kozmo', 'domain monarch', 'performapal', 'dracoslayer',
            'kaiju', 'phantom knight', 'metalfoe', 'crystal beast', 'ancient gear',
            'cyber dragon', 'gladiator beast', 'fire fist', 'mermail', 'madolche',
            'noble knight', 'bujin', 'geargia', 'sylvan', 'battlin boxer', 'ghostrick',
            'vampire', 'zombie', 'spellcaster', 'warrior', 'dragon', 'fiend', 'fairy',
            'machine', 'thunder', 'dinosaur', 'sea serpent', 'pyro', 'rock', 'winged beast'
        ]
        
        self.card_types = [
            'normal', 'effect', 'ritual', 'fusion', 'synchro', 'xyz', 'pendulum', 'link',
            'spell', 'trap', 'continuous', 'field', 'equip', 'quick-play', 'counter',
            'secret rare', 'ultra rare', 'super rare', 'rare', 'common', 'starlight',
            'ghost rare', 'ultimate rare', 'parallel rare', 'duel terminal'
        ]
    
    def extract_card_group(self, card_name):
        """Extrae el arquetipo principal de la carta Yu-Gi-Oh!"""
        normalized = self.normalize_text(card_name)
        
        best_match = None
        best_score = 0
        
        for archetype in self.archetypes:
            # Buscar coincidencia del arquetipo en el nombre
            if ' ' in archetype:
                # Para arquetipos de varias palabras (ej: "Blue-Eyes")
                archetype_words = archetype.replace('-', ' ').split()
                matches = 0
                for word in archetype_words:
                    if word in normalized:
                        matches += 1
                
                if matches >= len(archetype_words):
                    return archetype
                elif matches > 0:
                    score = (matches / len(archetype_words)) * 100
                    if score > best_score:
                        best_score = score
                        best_match = archetype
            else:
                # Para arquetipos de una palabra
                score = jaro_winkler_similarity(archetype, normalized) * 100
                if score > best_score and score >= 70:
                    best_score = score
                    best_match = archetype
        
        return best_match if best_score >= 60 else None
    
    def preprocess_card_name(self, name):
        """Preprocesamiento específico para cartas Yu-Gi-Oh!"""
        name = self.normalize_text(name)
        
        # Normalizar tipos de carta
        for card_type in self.card_types:
            pattern = rf'\b{re.escape(card_type)}\b'
            name = re.sub(pattern, card_type.upper(), name, flags=re.IGNORECASE)
        
        # Remover códigos de set (ej: LOB-001)
        name = re.sub(r'\b[A-Z]{3,4}-\d{3}\b', '', name)
        name = re.sub(r'\b[A-Z]{4,5}\d{5}\b', '', name)
        
        # Remover ediciones
        name = re.sub(r'\b(1st|unlimited|limited)\s*edition\b', '', name, flags=re.IGNORECASE)
        
        return re.sub(r'\s+', ' ', name).strip()

class MagicCardMatcher(BaseTCGMatcher):
    """Matcher específico para cartas Magic: The Gathering"""
    
    def __init__(self):
        super().__init__()
        # Nombres de cartas icónicas y palabras clave para agrupar
        self.card_names = [
            'lightning bolt', 'counterspell', 'dark ritual', 'giant growth',
            'ancestral recall', 'black lotus', 'mox', 'serra angel', 'shivan dragon',
            'llanowar elves', 'birds of paradise', 'sol ring', 'wrath of god',
            'brainstorm', 'force of will', 'tarmogoyf', 'snapcaster mage',
            'jace', 'liliana', 'chandra', 'garruk', 'elspeth', 'ajani', 'nissa',
            'gideon', 'vraska', 'teferi', 'karn', 'ugin', 'nicol bolas', 'eldrazi'
        ]
        
        self.card_types = [
            'instant', 'sorcery', 'creature', 'artifact', 'enchantment', 'planeswalker',
            'land', 'tribal', 'legendary', 'basic', 'snow', 'mythic rare', 'rare',
            'uncommon', 'common', 'foil', 'promo', 'extended art', 'borderless',
            'showcase', 'retro frame', 'full art'
        ]
        
        # Palabras clave para agrupar por mecánicas
        self.keywords = [
            'flying', 'trample', 'haste', 'vigilance', 'lifelink', 'deathtouch',
            'first strike', 'double strike', 'hexproof', 'shroud', 'indestructible',
            'flash', 'defender', 'reach', 'menace', 'prowess', 'scry', 'storm'
        ]
    
    def extract_card_group(self, card_name):
        """Extrae el grupo principal de la carta Magic"""
        normalized = self.normalize_text(card_name)
        
        # Buscar nombres de cartas específicas primero
        best_match = None
        best_score = 0
        
        for card in self.card_names:
            score = jaro_winkler_similarity(card, normalized) * 100
            if score > best_score and score >= 75:
                best_score = score
                best_match = card
        
        if best_match:
            return best_match
        
        # Si no hay match directo, agrupar por primera palabra significativa
        words = normalized.split()
        if words:
            # Filtrar palabras comunes que no son útiles para agrupar
            common_words = ['the', 'of', 'and', 'or', 'a', 'an', 'to', 'for', 'with']
            significant_words = [w for w in words if w not in common_words and len(w) > 2]
            
            if significant_words:
                return significant_words[0]
        
        return None
    
    def preprocess_card_name(self, name):
        """Preprocesamiento específico para cartas Magic"""
        name = self.normalize_text(name)
        
        # Normalizar tipos de carta
        for card_type in self.card_types:
            pattern = rf'\b{re.escape(card_type)}\b'
            name = re.sub(pattern, card_type.upper(), name, flags=re.IGNORECASE)
        
        # Remover códigos de set y números de colección
        name = re.sub(r'\b\d{1,3}/\d{1,3}\b', '', name)
        name = re.sub(r'\b[A-Z]{3}\d{3}\b', '', name)
        
        # Remover información de rareza redundante
        name = re.sub(r'\b(m|r|u|c)\b', '', name)
        
        return re.sub(r'\s+', ' ', name).strip()

class UniversalTCGMatcher:
    """Matcher universal que detecta automáticamente el tipo de TCG"""
    
    def __init__(self):
        self.pokemon_matcher = PokemonCardMatcher()
        self.yugioh_matcher = YugiohCardMatcher()
        self.magic_matcher = MagicCardMatcher()
    
    def detect_tcg_type(self, card_names):
        """Detecta automáticamente el tipo de TCG basado en los nombres de cartas"""
        sample_text = ' '.join(card_names[:20]).lower()  # Usar muestra de cartas
        
        pokemon_indicators = ['pokemon', 'pikachu', 'charizard', 'gx', 'ex', 'vmax']
        yugioh_indicators = ['yu-gi-oh', 'yugioh', 'spell', 'trap', 'xyz', 'synchro']
        magic_indicators = ['magic', 'mtg', 'planeswalker', 'instant', 'sorcery', 'mana']
        
        pokemon_score = sum(1 for indicator in pokemon_indicators if indicator in sample_text)
        yugioh_score = sum(1 for indicator in yugioh_indicators if indicator in sample_text)
        magic_score = sum(1 for indicator in magic_indicators if indicator in sample_text)
        
        if pokemon_score >= yugioh_score and pokemon_score >= magic_score:
            return 'pokemon'
        elif yugioh_score >= magic_score:
            return 'yugioh'
        else:
            return 'magic'
    
    def get_matcher(self, tcg_type):
        """Obtiene el matcher apropiado para el tipo de TCG"""
        matchers = {
            'pokemon': self.pokemon_matcher,
            'yugioh': self.yugioh_matcher,
            'magic': self.magic_matcher
        }
        return matchers.get(tcg_type.lower())
    
    def auto_match_cards(self, query_cards, candidate_cards, threshold=0.85, tcg_type=None):
        """Hace matching automático detectando el tipo de TCG"""
        
        if not tcg_type:
            tcg_type = self.detect_tcg_type(query_cards + candidate_cards)
        
        matcher = self.get_matcher(tcg_type)
        if not matcher:
            raise ValueError(f"TCG type '{tcg_type}' not supported")
        
        results = matcher.batch_match_cards(query_cards, candidate_cards, threshold)
        
        return {
            'tcg_detected': tcg_type,
            'matches': results,
            'groups': matcher.grouped_cards
        }

# Ejemplo de uso
if __name__ == "__main__":
    # Crear el matcher universal
    universal_matcher = UniversalTCGMatcher()
    
    # Ejemplos de cartas de diferentes TCGs
    pokemon_cards_a = [
        "Pikachu EX - Holo Rare",
        "Charizard GX Full Art", 
        "Mewtwo V - Secret Rare"
    ]
    
    pokemon_cards_b = [
        "Pikachu EX (Holográfica)",
        "Charizard-GX Arte Completo",
        "Mewtwo V Secreta"
    ]
    
    yugioh_cards_a = [
        "Blue-Eyes White Dragon - Ultra Rare",
        "Dark Magician - Secret Rare",
        "Red-Eyes Black Dragon"
    ]
    
    yugioh_cards_b = [
        "Blue Eyes White Dragon (Ultra)",
        "Dark Magician Secret",
        "Red Eyes B. Dragon"
    ]
    
    magic_cards_a = [
        "Lightning Bolt - Uncommon",
        "Jace, the Mind Sculptor",
        "Tarmogoyf - Mythic Rare"
    ]
    
    magic_cards_b = [
        "Lightning Bolt (U)",
        "Jace the Mind Sculptor",
        "Tarmogoyf Mythic"
    ]
    
    # Hacer matching automático para cada TCG
    tcgs = [
        ('Pokemon', pokemon_cards_a, pokemon_cards_b),
        ('Yu-Gi-Oh!', yugioh_cards_a, yugioh_cards_b),
        ('Magic', magic_cards_a, magic_cards_b)
    ]
    
    for tcg_name, cards_a, cards_b in tcgs:
        print(f"\n=== {tcg_name.upper()} ===")
        results = universal_matcher.auto_match_cards(cards_a, cards_b, threshold=0.80)
        
        print(f"TCG detectado: {results['tcg_detected']}")
        print("Matches encontrados:")
        
        for query, match in results['matches'].items():
            if match:
                print(f"  '{query}' -> '{match['card']}' (Score: {match['score']:.1f})")
            else:
                print(f"  '{query}' -> Sin match")
        
        print(f"Grupos creados: {len(results['groups'])}")