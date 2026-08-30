import unittest

import numpy as np
import pandas as pd

from src.inference.bootstrap import executar_bootstrap
from src.inference.ab_testing import executar_teste_permutacao, _extrair_grupos


class TestInferencia(unittest.TestCase):
    def setUp(self):
        self.base = pd.DataFrame({'energia_media': [10., 12., 11., 1., 2., 3., 6.],
                                  'nuvens_media': [0, 10, 30, 70, 80, 100, 50]})

    def test_bootstrap_media_desvio_e_ic_normal(self):
        r = executar_bootstrap(self.base, n_boot=2000, caminho_grafico=None)
        x = self.base['energia_media']
        self.assertAlmostEqual(r['media_amostral'], x.mean())
        self.assertAlmostEqual(r['desvio_padrao_amostral'], x.std(ddof=1))
        esperado = x.mean() + np.array([-1, 1]) * 1.96 * x.std(ddof=1) / np.sqrt(len(x))
        np.testing.assert_allclose(r['ic_normal_95'], esperado)
        np.testing.assert_allclose(r['ic_bootstrap_95'],
                                   np.percentile(r['medias_bootstrap'], [2.5, 97.5]))

    def test_bootstrap_reprodutivel(self):
        a = executar_bootstrap(self.base, n_boot=2000, caminho_grafico=None)
        b = executar_bootstrap(self.base, n_boot=2000, caminho_grafico=None)
        np.testing.assert_array_equal(a['medias_bootstrap'], b['medias_bootstrap'])

    def test_grupos_exclusivos_e_limites_inclusivos(self):
        a, b = _extrair_grupos(self.base)
        np.testing.assert_array_equal(a, [10, 12, 11])
        np.testing.assert_array_equal(b, [1, 2, 3])

    def test_permutacao_bicaudal_corrigida_e_reprodutivel(self):
        original = self.base.copy(deep=True)
        a = executar_teste_permutacao(self.base, n_perm=2000, caminho_grafico=None)
        b = executar_teste_permutacao(self.base, n_perm=2000, caminho_grafico=None)
        extremos = np.count_nonzero(np.abs(a['diferencas_permutadas']) >=
                                    abs(a['diferenca_observada']))
        self.assertAlmostEqual(a['p_valor'], (extremos + 1) / 2001)
        np.testing.assert_array_equal(a['diferencas_permutadas'], b['diferencas_permutadas'])
        pd.testing.assert_frame_equal(self.base, original)

    def test_rejeita_poucas_replicas(self):
        with self.assertRaises(ValueError):
            executar_bootstrap(self.base, n_boot=1999, caminho_grafico=None)
        with self.assertRaises(ValueError):
            executar_teste_permutacao(self.base, n_perm=1999, caminho_grafico=None)

    def test_rejeita_grupos_insuficientes(self):
        with self.assertRaises(ValueError):
            executar_teste_permutacao(self.base.iloc[:3], caminho_grafico=None)


if __name__ == '__main__':
    unittest.main()
