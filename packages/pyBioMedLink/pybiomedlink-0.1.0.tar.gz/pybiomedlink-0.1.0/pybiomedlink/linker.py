from abc import ABC, abstractmethod
from typing import List, Dict, Any


class BaseZSLinker(ABC):
    """
    Base class for all zero-shot linkers.

    These linkers do not require training.
    """
    @abstractmethod
    def predict(self, query: str, top_k: int) -> List[str]:
        """
        Predict the top-k linked entities/labels for a given query.
        """
        pass

    @abstractmethod
    def predict_aux(self, query: str, top_k: int) -> Dict[str, Any]:
        """
        Predict auxiliary information for the query.
        This can include additional scores or other information.
        """
        pass


class BM25Linker(BaseZSLinker):
    """
    BM25-based zero-shot linker.
    
    This linker uses the BM25 algorithm to link biomedical terms.
    """
    @staticmethod
    def tokenize(text: str) -> List[str]:
        """
        Tokenize the input text into a list of tokens.
        
        Args:
            text (str): The input text to tokenize.
        Returns:
            List[str]: A list of tokens.
        """
        # TODO: may use a more sophisticated tokenizer
        return text.split(" ")

    def __init__(self, labels: List[str]):
        """
        Args:
            labels (List[str]): List of labels/entities to link against.
        """
        from rank_bm25 import BM25Okapi
        tokenized_labels = [BM25Linker.tokenize(label) for label in labels]
        self.labels = labels
        self.model = BM25Okapi(tokenized_labels)

    def predict(self, query: str, top_k: int = 10) -> List[str]:
        """
        Predict the top-k linked entities for a given query.
        
        Args:
            query (str): The input query to link.
            top_k (int): The number of top results to return.
        Returns:
            List[str]: A list of top-k linked entities.
        """
        tokenized_query = BM25Linker.tokenize(query)
        return self.model.get_top_n(tokenized_query, self.labels, n=top_k)

    def predict_aux(self, query: str, top_k: int = 10) -> Dict[str, Any]:
        tokenized_query = BM25Linker.tokenize(query)
        label_scores = self.model.get_scores(tokenized_query)
        top_indices = label_scores.argsort(stable=True)[-top_k:][::-1]
        result = {
            "labels": [self.labels[i] for i in top_indices],
            "scores": [label_scores[i].item() for i in top_indices]
        }
        return result


class LevenshteinLinker(BaseZSLinker):
    """
    Levenshtein distance-based zero-shot linker.
    
    This linker uses the Levenshtein distance to link biomedical terms.
    Implementation adapted from https://www.nltk.org/_modules/nltk/metrics/distance.html#edit_distance_align
    """
    @staticmethod
    def _edit_dist_init(len1: int, len2: int) -> List[List[int]]:
        lev = []
        for i in range(len1):
            lev.append([0] * len2)  # initialize 2D array to zero
        for i in range(len1):
            lev[i][0] = i  # column 0: 0,1,2,3,4,...
        for j in range(len2):
            lev[0][j] = j  # row 0: 0,1,2,3,4,...
        return lev
    
    @staticmethod
    def _last_left_t_init(sigma: str):
        return {c: 0 for c in sigma}
    
    @staticmethod
    def _edit_dist_step(
        lev: List[List[int]], 
        i: int, 
        j: int, 
        s1: str, 
        s2: str, 
        last_left: int, 
        last_right: int, 
        substitution_cost: int = 1, 
        transpositions: bool = False
    ):
        c1 = s1[i - 1]
        c2 = s2[j - 1]

        # skipping a character in s1
        a = lev[i - 1][j] + 1
        # skipping a character in s2
        b = lev[i][j - 1] + 1
        # substitution
        c = lev[i - 1][j - 1] + (substitution_cost if c1 != c2 else 0)

        # transposition
        d = c + 1  # never picked by default
        if transpositions and last_left > 0 and last_right > 0:
            d = lev[last_left - 1][last_right - 1] + i - last_left + j - last_right - 1

        # pick the cheapest
        lev[i][j] = min(a, b, c, d)
    
    @staticmethod
    def edit_distance(
        s1: str, 
        s2: str, 
        substitution_cost: int = 1, 
        transpositions: bool = False):
        """
        Calculate the Levenshtein edit-distance between two strings.
        The edit distance is the number of characters that need to be
        substituted, inserted, or deleted, to transform s1 into s2.  For
        example, transforming "rain" to "shine" requires three steps,
        consisting of two substitutions and one insertion:
        "rain" -> "sain" -> "shin" -> "shine".  These operations could have
        been done in other orders, but at least three steps are needed.

        Allows specifying the cost of substitution edits (e.g., "a" -> "b"),
        because sometimes it makes sense to assign greater penalties to
        substitutions.

        This also optionally allows transposition edits (e.g., "ab" -> "ba"),
        though this is disabled by default.

        :param s1, s2: The strings to be analysed
        :param transpositions: Whether to allow transposition edits
        :type s1: str
        :type s2: str
        :type substitution_cost: int
        :type transpositions: bool
        :rtype: int
        """
        # set up a 2-D array
        len1 = len(s1)
        len2 = len(s2)
        lev = LevenshteinLinker._edit_dist_init(len1 + 1, len2 + 1)

        # retrieve alphabet
        sigma = set()
        sigma.update(s1)
        sigma.update(s2)

        # set up table to remember positions of last seen occurrence in s1
        last_left_t = LevenshteinLinker._last_left_t_init(sigma)

        # iterate over the array
        # i and j start from 1 and not 0 to stay close to the wikipedia pseudo-code
        # see https://en.wikipedia.org/wiki/Damerau%E2%80%93Levenshtein_distance
        for i in range(1, len1 + 1):
            last_right_buf = 0
            for j in range(1, len2 + 1):
                last_left = last_left_t[s2[j - 1]]
                last_right = last_right_buf
                if s1[i - 1] == s2[j - 1]:
                    last_right_buf = j
                LevenshteinLinker._edit_dist_step(
                    lev,
                    i,
                    j,
                    s1,
                    s2,
                    last_left,
                    last_right,
                    substitution_cost=substitution_cost,
                    transpositions=transpositions,
                )
            last_left_t[s1[i - 1]] = i
        return lev[len1][len2]

    def __init__(self, labels: List[str]):
        """
        Args:
            labels (List[str]): List of labels/entities to link against.
        """
        self.labels = labels
    
    def predict(self, query: str, top_k: int = 10) -> List[str]:
        lev_distances = [
            (label, LevenshteinLinker.edit_distance(query, label))
            for label in self.labels
        ]
        # Sort by distance, ascending
        lev_distances.sort(key=lambda x: x[1])
        # Return the top-k labels
        return [label for label, _ in lev_distances[:top_k]]

    def predict_aux(self, query: str, top_k: int = 10) -> Dict[str, Any]:
        lev_distances = [
            (label, LevenshteinLinker.edit_distance(query, label))
            for label in self.labels
        ]
        # Sort by distance, ascending
        lev_distances.sort(key=lambda x: x[1])
        results = {
            "labels": [label for label, _ in lev_distances[:top_k]],
            "scores": [distance for _, distance in lev_distances[:top_k]]
        }
        return results