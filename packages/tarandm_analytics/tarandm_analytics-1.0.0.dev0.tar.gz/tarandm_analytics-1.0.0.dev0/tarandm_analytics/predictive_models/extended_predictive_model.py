#   Exercise of exclusive rights to this Software belongs to Taran Advisory and distribution,
#   duplication or any other usage without previous written agreement of Taran Advisory is
#   prohibited.

from io import StringIO
from typing import Any, Dict, List, Optional, Union, cast

from pydantic import Field

from tarandm_analytics.predictive_models.expert_score import ModelExpertScore
from tarandm_analytics.predictive_models.extreme_gradient_boosting import ModelXGBoost
from tarandm_analytics.predictive_models.logistic_regression import ModelLogisticRegression
from tarandm_analytics.predictive_models.pmml_model import ModelPMML
from tarandm_analytics.predictive_models.random_forest import ModelRandomForest
from tarandm_analytics_utils.predictive_models.extended_predictive_model import (
    AbstractExtendedPredictiveModel,
    PredictiveModelType,
)
from tarandm_analytics_utils.utils.dump import safe_dumps_json


class ExtendedPredictiveModel(AbstractExtendedPredictiveModel):
    """
    PredictiveModel class is responsible for implementation of statistical models into TaranDM application.

    After initialization of the class, data about development of the models should be filled. For that fill_model_data
    function from tarandm_core/analytics/scorecard_support_functions/fill_scoring_model_object.py can be used. Before
    models implementation, ScoringModel object should be serialized into the Yaml file.
    """

    external_model: Union[ModelLogisticRegression, ModelXGBoost, ModelRandomForest, ModelExpertScore, ModelPMML] = (
        Field(..., discriminator="type", exclude=True)
    )

    def _migrate(self) -> None:
        if self.predictive_model_type == PredictiveModelType.EXPERT_SCORE:
            if len(self.external_model.feature_names) == 0:
                self.external_model.feature_names = self.attributes

    def get_external_model_stringio(self) -> StringIO:
        if self.predictive_model_type == PredictiveModelType.PMML:
            return StringIO(cast(ModelPMML, self.external_model).pmml_model)
        else:
            return StringIO(safe_dumps_json(self.external_model))

    def get_external_model_feature_names(self) -> Optional[List[str]]:
        return self.external_model.feature_names

    def get_external_model_intercept(self) -> Optional[float]:
        return self.external_model.intercept

    def get_external_model_intercept_name(self) -> Optional[str]:
        return self.external_model.intercept_name

    def get_external_model_coefficients(self) -> Optional[List[float]]:
        return self.external_model.coefficients

    def get_external_model_best_iteration(self) -> Optional[int]:
        if self.predictive_model_type == PredictiveModelType.XGB:
            try:
                model = cast(ModelXGBoost, self.external_model).model
                if model is None:
                    return None
                return model.best_iteration
            except AttributeError:
                return None
        return None

    def get_external_model_number_of_trees(self) -> Optional[int]:
        if self.predictive_model_type == PredictiveModelType.XGB:
            model = cast(ModelXGBoost, self.external_model).model
            if model is None:
                return None
            return model.num_boosted_rounds()
        return None

    def get_external_model_number_of_attributes(self) -> Optional[int]:
        if self.predictive_model_type == PredictiveModelType.XGB:
            model = cast(ModelXGBoost, self.external_model).model
            if model is None:
                return None
            return model.num_features()
        return None

    def get_external_model_best_eval_metric(self) -> Optional[float]:
        if self.predictive_model_type == PredictiveModelType.XGB:
            try:
                model = cast(ModelXGBoost, self.external_model).model
                if model is None:
                    return None
                return model.best_score
            except AttributeError:
                return None
        return None

    def get_data_for_shap_waterfall(
        self, original_attribute_values: Dict[str, Any], attribute_values: Dict[str, Any]
    ) -> Dict[str, Any]:
        from shap import TreeExplainer

        values = [attribute_values[val] for val in self.external_model.feature_names]
        if self.predictive_model_type == PredictiveModelType.XGB:
            explainer = TreeExplainer(cast(ModelXGBoost, self.external_model).model)
            shap_values = explainer([values])[0]
            return {
                "values": shap_values.values.tolist(),
                "base_value": shap_values.base_values.tolist(),
                "data": shap_values.data,
                "attributes": original_attribute_values,
                "feature_names": self.external_model.feature_names,
            }
        elif self.predictive_model_type == PredictiveModelType.LOGISTIC_REGRESSION:
            mc = []
            i = 0
            for val in values:
                mc.append(val * self.external_model.model.coef_[0][i])  # type: ignore
                i += 1

            return {
                "values": mc,
                "base_value": float(self.external_model.model.intercept_[0]),  # type: ignore
                "data": values,
                "attributes": original_attribute_values,
                "feature_names": self.external_model.feature_names,
            }
        elif self.predictive_model_type == PredictiveModelType.EXPERT_SCORE:
            return {
                "values": values,
                "base_value": self.external_model.intercept or 0.0,
                "data": [original_attribute_values[val] for val in self.external_model.feature_names],
                "attributes": original_attribute_values,
                "feature_names": self.external_model.feature_names,
            }

        return {}
