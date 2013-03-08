from lib.test import Shaman

class Dunno(Shaman):

    @Shaman.generate(
        A=('A', 'supercalifragilisticexpialidocious', 'Support staff hung over, send aspirin and come back LATER.'),
        B=('B', 'floopdy whoopdy doobedo', 'Your/our computer(s) had suffered a memory leak, and we are waiting for them to be topped up.'),
        C=('C', 'scooby dooby doo', 'short leg on process table')
    )
    def test(self, letter, request, expected):
        self.web.route(
            'http://pages.cs.wisc.edu/~ballard/bofh/bofhserver.pl',
            file='%s.html' % letter
        )
        result = self.query(request)
        self.assertLooksLike(result[len(result)-len(expected):], expected)
