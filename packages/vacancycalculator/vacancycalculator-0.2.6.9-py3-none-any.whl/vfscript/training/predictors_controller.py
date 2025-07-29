import json
import pandas as pd
from sklearn.tree import DecisionTreeClassifier, export_text
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

class VacancyClassifier:
    def __init__(self,
                 json_file1: str,
                 json_file2: str,
                 merged_json: str,
                 csv_input: str,
                 csv_output: str,
                 max_depth: int = 5,
                 min_samples_leaf: int = 3):
        """
        Inicializa rutas y parámetros del clasificador.
        """
        self.json_file1 = json_file1
        self.json_file2 = json_file2
        self.merged_json = merged_json
        self.csv_input = csv_input
        self.csv_output = csv_output
        self.max_depth = max_depth
        self.min_samples_leaf = min_samples_leaf
        self.clf = None

    def merge_json(self):
        """
        Combina los dos JSON de entrenamiento en un solo archivo.
        """
        with open(self.json_file1, 'r') as f1:
            data1 = json.load(f1)
        with open(self.json_file2, 'r') as f2:
            data2 = json.load(f2)

        merged = {}
        for key in set(data1.keys()) | set(data2.keys()):
            merged[key] = data1.get(key, []) + data2.get(key, [])

        with open(self.merged_json, 'w') as fout:
            json.dump(merged, fout, indent=4)
        print(f"Merged JSON saved to: {self.merged_json}")

    @staticmethod
    def _label_category(vacancys: int) -> str:
        """
        Retorna la categoría según vacancys: "1-4", "5-10" o "11-15".
        """
        if 1 <= vacancys <= 4:
            return "1-4"
        elif 5 <= vacancys <= 10:
            return "5-10"
        elif 11 <= vacancys <= 15:
            return "11-15"
        return None

    def train(self):
        """
        Entrena el Decision Tree usando solo la característica "cluster_size".
        """
        with open(self.merged_json, 'r') as f:
            data = json.load(f)
        df = pd.DataFrame(data)
        df['category'] = df['vacancys'].apply(self._label_category)
        df = df[df['category'].notna()]

        # Usar únicamente cluster_size como predictor
        X = df[['cluster_size']]
        y = df['category']

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )

        self.clf = DecisionTreeClassifier(
            criterion='gini',
            max_depth=self.max_depth,
            min_samples_leaf=self.min_samples_leaf,
            random_state=0
        )
        self.clf.fit(X_train, y_train)
        print("Training completed using only 'cluster_size'.")

        # Evaluación
        y_pred = self.clf.predict(X_test)
        print("Classification report:\n", classification_report(y_test, y_pred))
        print("Tree structure:\n", export_text(self.clf, feature_names=['cluster_size']))

    def classify_defects(self):
        """
        Clasifica cada defecto del CSV de entrada usando solo "cluster_size" y evita warnings por nombres de features.
        """
        if self.clf is None:
            raise ValueError("El modelo no está entrenado. Llama a train() primero.")

        df_defects = pd.read_csv(self.csv_input)

        def _predict(row):
            # Crear DataFrame temporal con columna 'cluster_size'
            df_temp = pd.DataFrame([[row['cluster_size']]], columns=['cluster_size'])
            return self.clf.predict(df_temp)[0]

        df_defects['category_predicted'] = df_defects.apply(_predict, axis=1)
        df_defects.to_csv(self.csv_output, index=False)
        print(f"Defects classified using 'cluster_size'. Output saved to: {self.csv_output}")


