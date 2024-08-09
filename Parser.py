from rdflib import Graph, URIRef
import spacy
from nltk.corpus import wordnet
import itertools

nlp = spacy.load("en_core_web_sm")


class MySPARQL:
    def __init__(self, ontology_file):
        self.ontology_file = ontology_file

        self.g = Graph()
        self.g.parse(self.ontology_file, format='turtle')
        self.tags = URIRef('http://www.w3.org/2000/01/rdf-schema#tags')

    def search_label(self, search_term):
        results = []
        query = f"""
            SELECT DISTINCT ?subject ?superClass ?label ?comment ?seeAlso ?tags
            WHERE{{
                ?subject rdf:type owl:Class; rdfs:label ?label .
                OPTIONAL{{?subject rdfs:subClassOf ?superClass; rdfs:label ?label}} .
                OPTIONAL{{?subject rdfs:comment ?comment}} .
                OPTIONAL{{?subject rdfs:seeAlso ?seeAlso}} .
                FILTER regex(?label, "{search_term}")
            }}
            """
        qres = self.g.query(query)

        for item in self.get_subclass(qres):
            results.append(item)

        keywords = ''
        scored_results = self.calculate_score(keywords, self.remove_duplicates(results))
        scored_results.sort(key=lambda x: x[6], reverse=True)

        return scored_results

    def search(self, search_term):

        result = []
        keywords = self.extract_keywords(search_term)
        for query_term in keywords:
            query = f"""
                SELECT DISTINCT ?subject ?superClass ?label ?comment ?seeAlso ?tags
                WHERE{{
                    ?subject rdf:type owl:Class; rdfs:label ?label .
                    OPTIONAL{{?subject rdfs:subClassOf ?superClass; rdfs:label ?label}} .
                    OPTIONAL{{?subject rdfs:comment ?comment}} .
                    OPTIONAL{{?subject rdfs:seeAlso ?seeAlso}} .
                    OPTIONAL{{?subject rdfs:tags ?tags}} .
                    FILTER (regex(?label, "{query_term}") || (regex(?comment, "{query_term}")) || (regex(?tags, "{query_term}"))) 
                }}
                ORDER BY ?label
                """

            qres = self.g.query(query)
            for item in self.get_subclass(qres):
                result.append(item)

        scored_results = self.calculate_score(keywords, self.remove_duplicates(result))
        scored_results.sort(key=lambda x: x[6], reverse=True)

        # for item in scored_results:
        #     print(f"{item[0]} has score {item[6]}")
        #
        return scored_results

    def get_subclass(self, qres):

        result = []
        for row in qres:
            query2 = f"""
                    SELECT DISTINCT ?subject ?superClass ?label
                    WHERE{{
                        ?subject rdf:type owl:Class; rdfs:subClassOf ?superClass; rdfs:label ?label 
                        FILTER regex(str(?superClass), "{row.subject}")
                    }}
                    """

            qres2 = self.g.query(query2)

            subclass = []
            for row2 in qres2:
                subclass.append(str(row2.subject.replace("_", " ")).rsplit('#', 1)[-1])

            result.append([row.label, row.comment, row.seeAlso, row.tags,
                           (str(row.superClass).rsplit('#', 1)[-1]).replace("_", " "), subclass])

        return result

    def get_instances(self, label):
        instances = []

        query3 = f"""
                SELECT DISTINCT ?class_label ?individual_label ?comment ?seeAlso
                WHERE{{
                        ?x rdf:type owl:NamedIndividual; rdfs:label ?individual_label; rdf:type ?y .
                        ?y rdfs:label ?class_label
                        OPTIONAL{{?x rdfs:comment ?comment}} .
                        OPTIONAL{{?x rdfs:seeAlso ?seeAlso}} .
                        FILTER (?class_label="{label}")
                }}
                """
        qres = self.g.query(query3)
        for row in qres:
            instances.append([row.individual_label, row.comment, row.seeAlso])
        return instances

    def calculate_score(self, keywords_list, results):
        lowered_keywords_list = [keyword.lower() for keyword in keywords_list]

        new_keywords_list = list(set(lowered_keywords_list))  # removes duplicate words
        for i in range(len(results)):

            labelScore, tagsScore, commentScore, superScore, subScore = 0, 0, 0, 0, 0

            for keyword in new_keywords_list:
                labelScore += str(results[i][0]).lower().count(keyword)
                if str(results[i][0].lower()) == keyword:
                    labelScore += 10
                tagsScore += str(results[i][3]).lower().count(keyword)
                commentScore += str(results[i][1]).lower().count(keyword)
                for superClass in results[i][4]:
                    superScore += superClass.lower().count(keyword)

                for subClass in results[i][5]:
                    subScore += subClass.lower().count(keyword)

            totalScore = 3.0 * labelScore + 6.0 * tagsScore + 1.0 * commentScore + 1.0 * superScore + 1.0 * subScore
            results[i].append(totalScore)
        return results

    def get_synonyms(self, word):
        synonyms = set()
        for syn in wordnet.synsets(word):
            synonyms.update(lemma.name() for lemma in syn.lemmas())
        return list(synonyms)

    def extract_keywords(self, query):
        keywords = set()
        doc = nlp(query)
        lemmatized_words = [token.lemma_ for token in doc if not token.is_stop]
        noun_chunks = [chunk.text for chunk in doc.noun_chunks]
        kw = [word for word in lemmatized_words + noun_chunks if word.lower() not in nlp.Defaults.stop_words]
        for item in kw:
            keywords.add(item)

        for word in list(keywords):
            for synonym in self.get_synonyms(word):
                keywords.add(synonym)

        # remove the underscores
        removed_underscore = []
        for word in list(keywords):
            removed_underscore.append(word.replace("_", " ").split())

        return list(set(self.flatten_extend(removed_underscore)))

    def flatten_extend(self, matrix):
        flat_list = []
        for row in matrix:
            flat_list.extend(row)
        return flat_list

    def remove_duplicates(self, result_list):
        result_list.sort()
        return list(results for results, _ in itertools.groupby(result_list))


if __name__ == "__main__":
    q = MySPARQL("ISSTO.owl")

    while True:
        user_query = input("Enter the information you are searching for (or 'exit' to quit): ")

        result = q.get_instances(user_query)
        for item in result:
            print(f"{item[0]}\n\n{item[1]}")
        if user_query.lower() == 'exit':
            break
