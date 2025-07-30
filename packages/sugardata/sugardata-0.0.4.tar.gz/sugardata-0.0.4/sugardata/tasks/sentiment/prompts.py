from ...components.translator import Translator


def get_dimension_prompt(language: str) -> str:

    DIMENSION_PROMPTS = {
        "en": """
                You are an expert in ontology design, knowledge representation, and concept hierarchy analysis.
                You will be given a concept and your task is to generate dimensions, sub fields, subcategories, and related concepts for that concept.
                You must generate at least 10 dimensions, ensuring a mix of hierarchical subcategories and adjacent concepts.
                
                ############
                Concept: {concept}

                Format Instructions:
                {format_instructions}
            """,
        "tr":"""
                Ontoloji tasarımı, bilgi temsili ve kavram hiyerarşisi analizi konusunda uzman birisiniz.
                Size bir kavram verilecek ve göreviniz bu kavram için boyutlar, alt alanlar, alt kategoriler ve ilgili kavramlar üretmektir.
                En az 10 boyut üretmelisiniz, hiyerarşik alt kategoriler ve ilgili kavramlar arasında bir karışım sağlamak için.
                Alt kategoriler (kavramın altında yer alanlar) ve ilgili kavramlar (yaratıcı bağlantılar kuranlar) arasında net bir ayrım yapmalısınız.

                ############
                Kavram: {concept}
                Format Talimatları:
                {format_instructions}
            """
    }

    text = DIMENSION_PROMPTS.get(language)

    if not text:
        core_text = DIMENSION_PROMPTS["en"].split("############")[0]
        translated_core_text = Translator.translate(core_text, target_language=language, source_language="en", vendor="deep-translator")
        text = translated_core_text + DIMENSION_PROMPTS["en"].split("############")[1]

    return text


def get_aspect_prompt(language: str) -> str:
    ASPECT_PROMPTS = {
        "en": """
                You are an expert in ontology design, knowledge representation, and concept hierarchy analysis.
                You will be given a concept and its a specific dimension (or subcategory) and your task is to generate aspects for that concept.

                ############
                Index: {index}
                Concept: {concept}
                Dimension: {dimension}

                Format Instructions:
                {format_instructions}
            """,
        "tr": """
                Ontoloji tasarımı, bilgi temsili ve kavram hiyerarşisi analizi konusunda uzman birisiniz.
                Size bir kavram ve onun belirli bir boyutu (veya alt kategorisi) verilecek ve göreviniz bu kavram için yönleri üretmektir.

                ############
                İndeks: {index}
                Kavram: {concept}
                Boyut: {dimension}

                Format Talimatları:
                {format_instructions}
            """
    }

    text = ASPECT_PROMPTS.get(language)

    if not text:
        core_text = ASPECT_PROMPTS["en"].split("############")[0]
        translated_core_text = Translator.translate(core_text, target_language=language, source_language="en", vendor="deep-translator")
        text = translated_core_text + ASPECT_PROMPTS["en"].split("############")[1]
    return text


def get_sentence_prompt(language: str) -> str:
    SENTENCE_PROMPTS = {
        "en": """
                You are a creative writing assistant. Generate vivid, sentiment-rich text that expresses the required sentiment toward the given aspect of a concept.

                TASK: Write a short, creative snippet that clearly shows the specified sentiment about the given aspect.

                REQUIREMENTS:
                - Express the sentiment toward the aspect unmistakably
                - Use the specified writing style and medium conventions
                - Include at least 2 rhetorical devices (metaphor, alliteration, etc.)
                - Reference the aspect explicitly at least once
                - Keep language natural, avoid clichés
                - Length: approximately given sentence length sentences
                - DO NOT copy phrases from previous responses; use fresh metaphors and imagery
                - Prioritize: 1) Medium conventions, 2) Aspect-Sentiment clarity, 3) Other parameters

                RESPOND WITH VALID JSON ONLY:
                {{
                "index": "index",
                "generated_text": "your creative text here"
                }}

                ############
                PARAMETERS:
                - Index: {index}
                - Concept: {concept}
                - Aspect: {aspect}
                - Writing Style: {writing_style}
                - Medium: {medium}
                - Persona: {persona}
                - Intention: {intention}
                - Sentence Length: {sentence_length}

                OUTPUT FORMAT: {format_instructions}
                """,
        "tr": """
                Yaratıcı bir yazma asistanısınız. Verilen kavramın belirli bir yönüne yönelik duygu zengin metin üretin.
                GÖREV: Belirtilen yön hakkında açıkça gösteren kısa, yaratıcı bir parça yazın.
                GEREKSİNİMLER:
                - Yön hakkında duygu açıkça ifade edilmeli
                - Belirtilen yazım stili ve ortam kurallarına uyulmalı
                - En az 2 retorik araç (metafor, aliterasyon vb.) kullanılmalı
                - Yön en az bir kez açıkça referans edilmeli
                - Dili doğal tutun, klişelerden kaçının
                - Uzunluk: yaklaşık verilen cümle uzunluğu cümlesi
                - Önceki yanıtlardan cümle kopyalamayın; taze metaforlar ve imgeler kullanın
                - Öncelik: 1) Ortam kuralları, 2) Yön-Duygu netliği, 3) Diğer parametreler

                YALNIZCA GEÇERLİ JSON İLE CEVAP VERİN:
                {{
                "index": "index",
                "generated_text": "buraya yaratıcı metni yazın"
                }}

                ############
                PARAMETRELER:
                - İndeks: {index}
                - Kavram: {concept}
                - Yön: {aspect}
                - Yazım Stili: {writing_style}
                - Ortam: {medium}
                - Persona: {persona}
                - Niyet: {intention}
                - Cümle Uzunluğu: {sentence_length}
                ÇIKTI FORMAT: {format_instructions}
                """
    }

    text = SENTENCE_PROMPTS.get(language)

    if not text:
        core_text = SENTENCE_PROMPTS["en"].split("############")[0]
        translated_core_text = Translator.translate(core_text, target_language=language, source_language="en", vendor="deep-translator")
        text = translated_core_text + SENTENCE_PROMPTS["en"].split("############")[1]   
    return text


def get_augment_sentence_prompt(language: str) -> str:
    AUGMENT_SENTENCE_PROMPTS = {
        "en": """
                You are a creative writing assistant. Generate vivid, sentiment-rich text that expresses the required sentiment toward the given aspect of a concept.

                TASK: Write a short, creative snippet that clearly shows the specified sentiment about the given aspect.

                REQUIREMENTS:
                - Express the sentiment toward the aspect unmistakably
                - Use the specified writing style and medium conventions
                - Include at least 2 rhetorical devices (metaphor, alliteration, etc.)
                - Reference the aspect explicitly at least once
                - Keep language natural, avoid clichés
                - Length: approximately given sentence length sentences

                RESPOND WITH VALID JSON ONLY:
                {{
                "index": "index",
                "generated_text": "your creative text here"
                }}
                ############
                PARAMETERS:
                - Index: {index}
                - Concept: {concept}
                - Aspect: {aspect}
                - Writing Style: {writing_style}
                - Medium: {medium}
                - Persona: {persona}
                - Intention: {intention}
                - Sentence Length: {sentence_length}
                - Given Text: {given_text}

                OUTPUT FORMAT: {format_instructions}
                """,
        "tr": """
                Yaratıcı bir yazma asistanısınız. Verilen kavramın belirli bir yönüne yönelik duygu zengin metin üretin.
                GÖREV: Belirtilen yön hakkında açıkça gösteren kısa, yaratıcı bir parça yazın.
                GEREKSİNİMLER:
                - Yön hakkında duygu açıkça ifade edilmeli
                - Belirtilen yazım stili ve ortam kurallarına uyulmalı
                - En az 2 retorik araç (metafor, aliterasyon vb.) kullanılmalı
                - Yön en az bir kez açıkça referans edilmeli
                - Dili doğal tutun, klişelerden kaçının
                - Uzunluk: yaklaşık verilen cümle uzunluğu cümlesi
                YALNIZCA GEÇERLİ JSON İLE CEVAP VERİN:
                {{
                "index": "index",
                "generated_text": "buraya yaratıcı metni yazın"
                }}  
                ############
                PARAMETRELER:
                - İndeks: {index}
                - Kavram: {concept}
                - Yön: {aspect} 
                - Yazım Stili: {writing_style}
                - Ortam: {medium}
                - Persona: {persona}
                - Niyet: {intention}
                - Cümle Uzunluğu: {sentence_length}
                - Verilen Metin: {given_text}

                ÇIKTI FORMAT: {format_instructions}
                """
    }

    text = AUGMENT_SENTENCE_PROMPTS.get(language)

    if not text:
        core_text = AUGMENT_SENTENCE_PROMPTS["en"].split("############")[0]
        translated_core_text = Translator.translate(core_text, target_language=language, source_language="en", vendor="deep-translator")
        text = translated_core_text + AUGMENT_SENTENCE_PROMPTS["en"].split("############")[1]   
    return text


def get_structure_prompt(language: str) -> str:
    STRUCTURE_PROMPTS = {
        "en": """
                You are an expert on extracting structured information from text.
                Your task is to analyze the provided text and extract structured information from it.
                The attributes you need to extract are:
                1. Concept: The main concept for which the sentiment is being analyzed.
                2. Aspects: The aspects related to the concept, which can have multiple derivatives. Only the aspects that the text is about should be extracted. Don't create hypothetical aspects. If not clear, just say "general".
                3. Writing Style: The writing style used in the generated text.
                4. Medium: The medium for which the text is generated.
                5. Persona: The persona of the writer.
                6. Intention: The intention behind the text.
                7. Sentence Length: The length of the sentences used in the text.
                8. Given Text: The text provided as input for structure extraction.

                Don't hypothetically create any information, just extract the information from the text.

                #############
                Text: {text}

                Format Instructions:
                {format_instructions}
            """,
        "tr": """
                Metinden yapılandırılmış bilgi çıkarma konusunda uzman birisiniz.
                Göreviniz, verilen metni analiz etmek ve yapılandırılmış bilgi çıkarmaktır.
                Çıkarmanız gereken öznitelikler şunlardır:
                1. Kavram: Duygunun analiz edildiği ana kavram.
                2. Yönler: Kavramla ilgili yönler, her yönün birden fazla türevi olabilir. Metnin ilgili olduğu yönleri çıkarmalısınız. Hipotetik yönler oluşturmayın. Net değilse, sadece "genel" olarak belirtin.
                3. Yazım Stili: Üretilen metinde kullanılan yazım stili.
                4. Ortam: Metnin hedeflendiği ortam.
                5. Persona: Yazarın karakteri.
                6. Niyet: Metnin arkasındaki niyet.
                7. Cümle Uzunluğu: Metinde kullanılan cümlelerin uzunluğu.
                8. Verilen Metin: Yapılandırma çıkarımı için verilen metin.

                Hipotetik olarak herhangi bir bilgi oluşturmayın, sadece metinden bilgiyi çıkarın.

                #############
                Metin: {text}

                Format Talimatları:
                {format_instructions}
            """
    }
    text = STRUCTURE_PROMPTS.get(language)

    if not text:
        core_text = STRUCTURE_PROMPTS["en"].split("#############")[0]
        translated_core_text = Translator.translate(core_text, target_language=language, source_language="en", vendor="deep-translator")
        text = translated_core_text + STRUCTURE_PROMPTS["en"].split("#############")[1]     
    return text

