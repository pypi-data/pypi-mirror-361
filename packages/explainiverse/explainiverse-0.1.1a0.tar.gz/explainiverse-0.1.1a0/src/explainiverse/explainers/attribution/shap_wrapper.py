# src/explainiverse/explainers/attribution/shap_wrapper.py

import shap
import numpy as np

from explainiverse.core.explainer import BaseExplainer
from explainiverse.core.explanation import Explanation


class ShapExplainer(BaseExplainer):
    """
    SHAP explainer (KernelSHAP-based) for model-agnostic explanations.
    """

    def __init__(self, model, background_data, feature_names, class_names):
        """
        Args:
            model: A model adapter with a .predict method.
            background_data: A 2D numpy array used as SHAP background distribution.
            feature_names: List of feature names.
            class_names: List of class labels.
        """
        super().__init__(model)
        self.feature_names = feature_names
        self.class_names = class_names
        self.explainer = shap.KernelExplainer(model.predict, background_data)


    def explain(self, instance, top_labels=1):
        """
        Generate SHAP explanation for a single instance.

        Args:
            instance: 1D numpy array of input features.
            top_labels: Number of top classes to explain (default: 1)

        Returns:
            Explanation object
        """
        instance = np.array(instance).reshape(1, -1)  # Ensure 2D
        shap_values = self.explainer.shap_values(instance)

        if isinstance(shap_values, list):
            # Multi-class: list of arrays, one per class
            predicted_probs = self.model.predict(instance)[0]
            top_indices = np.argsort(predicted_probs)[-top_labels:][::-1]
            label_index = top_indices[0]
            label_name = self.class_names[label_index]
            class_shap = shap_values[label_index][0]
        else:
            # Single-class (regression or binary classification)
            label_index = 0
            label_name = self.class_names[0] if self.class_names else "class_0"
            class_shap = shap_values[0]

            flat_shap = np.array(class_shap).flatten()
            attributions = {
                fname: float(flat_shap[i])
                for i, fname in enumerate(self.feature_names)
            }

        return Explanation(
            explainer_name="SHAP",
            target_class=label_name,
            explanation_data={"feature_attributions": attributions}
        )