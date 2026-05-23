class RegraDeNegocioError(Exception):
    def __init__(self, detail: str):
        self.detail = detail
        super().__init__(self.detail)

class CredenciaisInvalidasError(Exception):
    def __init__(self, detail: str):
        self.detail = detail
        super().__init__(self.detail)

class RecursoNaoEncontradoError(Exception):
    def __init__(self, detail: str):
        self.detail = detail
        super().__init__(self.detail)
