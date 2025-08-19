Este projeto implementa um pipeline completo de MLOps de ponta a ponta para previsão de rotatividade de clientes na nuvem AWS. Ele automatiza todo o ciclo de vida do aprendizado de máquina, desde a ingestão de dados e o treinamento do modelo até a implantação e o monitoramento. A arquitetura foi projetada para ser robusta, escalável e sustentável, utilizando uma stack de MLOps moderna.



Pipeline de ML automatizado: um pipeline do SageMaker é acionado automaticamente quando novos dados são carregados em um bucket S3.

Rastreamento de experimentos: um servidor MLflow, em execução em um cluster Kubernetes (EKS), rastreia todos os experimentos, incluindo parâmetros, métricas e artefatos do modelo.

Treinamento robusto do modelo: um modelo XGBoost é treinado com rastreamento abrangente de hiperparâmetros e artefatos.

Governança do modelo: o Registro de modelos do SageMaker é usado para versionar modelos e inclui uma etapa de aprovação manual antes da implantação.

Implantação escalável: o modelo aprovado é servido como uma API REST usando FastAPI em um cluster EKS, garantindo alta disponibilidade e escalabilidade.

Automação de CI/CD: as ações do GitHub são configuradas para automatizar os processos de compilação e implantação, acionadas por alterações no repositório.

Interface web: um painel de controle intuitivo (espaço reservado para extensão) permite previsões em tempo real.