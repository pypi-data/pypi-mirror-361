"""
Forge Links - A Python-Markdown Extension.

BSD License

Copyright (c) 2025 Tobias Bölz

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this
list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice,
this list of conditions and the following disclaimer in the documentation
and/or other materials provided with the distribution.

3. Neither the name of the copyright holder nor the names of its contributors
may be used to endorse or promote products derived from this software without
specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS “AS IS”
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

Copyright (c) 2017-2018 by Waylan Limberg. All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

*   Redistributions of source code must retain the above copyright
    notice, this list of conditions and the following disclaimer.
*   Redistributions in binary form must reproduce the above copyright
    notice, this list of conditions and the following disclaimer in the
    documentation and/or other materials provided with the distribution.
*   Neither the name of HTMLTree nor the names of its contributors may be
    used to endorse or promote products derived from this software without
    specific prior written permission.

THIS SOFTWARE IS PROVIDED BY WAYLAN LIMBERG ''AS IS'' AND ANY
EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL ANY CONTRIBUTORS TO Github-Links Extension
BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
POSSIBILITY OF SUCH DAMAGE.
"""

import unittest

from markdown import markdown

from mdx_forge_links import ForgeLinks


class TestForgeLinks(unittest.TestCase):
    maxDiff = None

    def assertMarkdownRenders(self, source, expected, **kwargs):
        """Test that source Markdown text renders to expected output."""
        configs = {
            'user': 'tmb',
            'repo': 'mdx-forge-links',
            'base_url': 'https://git.boelz.eu',
        }
        configs.update(kwargs)
        output = markdown(source, extensions=[ForgeLinks(**configs)])
        self.assertMultiLineEqual(output, expected)

    # Issue Tests
    def test_issue(self):
        self.assertMarkdownRenders(
            'Issue #123.',
            '<p>Issue <a class="forge-link forge-issue" '
            'href="https://git.boelz.eu/tmb/mdx-forge-links/issues/123" '
            'title="Issue tmb/mdx-forge-links #123">#123</a>.</p>',
        )

    def test_issue_leading_zero(self):
        self.assertMarkdownRenders(
            'Issue #012.',
            '<p>Issue <a class="forge-link forge-issue" '
            'href="https://git.boelz.eu/tmb/mdx-forge-links/issues/12" '
            'title="Issue tmb/mdx-forge-links #12">#012</a>.</p>',
        )

    def test_non_issue(self):
        self.assertMarkdownRenders(
            'Issue #notanissue.',
            '<p>Issue #notanissue.</p>',
        )

    def test_issue_with_repo(self):
        self.assertMarkdownRenders(
            'Issue Organization/Repo#123.',
            '<p>Issue <a class="forge-link forge-issue" '
            'href="https://git.boelz.eu/Organization/Repo/issues/123" '
            'title="Issue Organization/Repo #123">Organization/Repo#123</a>.</p>',
        )

    def test_issue_leading_zero_with_repo(self):
        self.assertMarkdownRenders(
            'Issue Organization/Repo#012.',
            '<p>Issue <a class="forge-link forge-issue" '
            'href="https://git.boelz.eu/Organization/Repo/issues/12" '
            'title="Issue Organization/Repo #12">Organization/Repo#012</a>.</p>',
        )

    def test_non_issue_with_repo(self):
        self.assertMarkdownRenders(
            'Issue Organization/Repo#notanissue.',
            '<p>Issue Organization/Repo#notanissue.</p>',
        )

    def test_escaped_issue(self):
        self.assertMarkdownRenders(
            'Issue \\#123.',
            '<p>Issue #123.</p>',
        )

    def test_escaped_issue_with_repo(self):
        self.assertMarkdownRenders(
            'Issue Organization/Repo\\#123.',
            '<p>Issue Organization/Repo#123.</p>',
        )

    def test_issue_in_link(self):
        self.assertMarkdownRenders(
            '[Issue #123](#).',
            '<p><a href="#">Issue #123</a>.</p>',
        )

    # Mention Tests
    def test_mention_user(self):
        self.assertMarkdownRenders(
            'User @foo.',
            '<p>User <a class="forge-link forge-mention" '
            'href="https://git.boelz.eu/foo" '
            'title="User: @foo">@foo</a>.</p>',
        )

    def test_mention_complex_user(self):
        self.assertMarkdownRenders(
            'User @Foo_Bar-42.',
            '<p>User <a class="forge-link forge-mention" '
            'href="https://git.boelz.eu/Foo_Bar-42" '
            'title="User: @Foo_Bar-42">@Foo_Bar-42</a>.</p>',
        )

    def test_escape_mention_user(self):
        self.assertMarkdownRenders(
            'User \\@foo.',
            '<p>User @foo.</p>',
        )

    def test_mention_repo(self):
        self.assertMarkdownRenders(
            'User @foo/bar.',
            '<p>User <a class="forge-link forge-mention" '
            'href="https://git.boelz.eu/foo/bar" '
            'title="Repository: @foo/bar">@foo/bar</a>.</p>',
        )

    def test_mention_repo_complex(self):
        self.assertMarkdownRenders(
            'User @foo/bar_baz-42.0.',
            '<p>User <a class="forge-link forge-mention" '
            'href="https://git.boelz.eu/foo/bar_baz-42.0" '
            'title="Repository: @foo/bar_baz-42.0">@foo/bar_baz-42.0</a>.</p>',
        )

    def test_escape_mention_repo(self):
        self.assertMarkdownRenders(
            'User \\@foo/bar.',
            '<p>User @foo/bar.</p>',
        )

    def test_mention_in_link(self):
        self.assertMarkdownRenders(
            'User [@foo](#).',
            '<p>User <a href="#">@foo</a>.</p>',
        )

    # Commit Tests
    def test_commit(self):
        self.assertMarkdownRenders(
            'Commit 83fb46b3b7ab8ad4316681fc4637c521da265f1d.',
            '<p>Commit <a class="forge-link forge-commit" '
            'href="https://git.boelz.eu/tmb/mdx-forge-links/commit/'
            '83fb46b3b7ab8ad4316681fc4637c521da265f1d" '
            'title="Commit: tmb/mdx-forge-links'
            '@83fb46b3b7ab8ad4316681fc4637c521da265f1d"'
            '>83fb46b</a>.</p>',
        )

    def test_commit_user(self):
        self.assertMarkdownRenders(
            'Commit foo@15abb8b3b02df0e380e9b4c71f3bd206c9751a93.',
            '<p>Commit <a class="forge-link forge-commit" '
            'href="https://git.boelz.eu/foo/mdx-forge-links/commit/'
            '15abb8b3b02df0e380e9b4c71f3bd206c9751a93" '
            'title="Commit: foo/mdx-forge-links'
            '@15abb8b3b02df0e380e9b4c71f3bd206c9751a93">foo@15abb8b</a>.</p>',
        )

    def test_commit_user_repo(self):
        self.assertMarkdownRenders(
            'Commit foo/bar@a75944f869d728ca9bc5472daf3f249b6c341308.',
            '<p>Commit <a class="forge-link forge-commit" '
            'href="https://git.boelz.eu/foo/bar/commit/'
            'a75944f869d728ca9bc5472daf3f249b6c341308" '
            'title="Commit: foo/bar@a75944f869d728ca9bc5472daf3f249b6c341308">foo/bar'
            '@a75944f</a>.</p>',
        )

    def test_escape_commit(self):
        self.assertMarkdownRenders(
            'Commit `83fb46b3b7ab8ad4316681fc4637c521da265f1d`.',
            '<p>Commit <code>83fb46b3b7ab8ad4316681fc4637c521da265f1d</code>.</p>',
        )

    def test_commit_in_link(self):
        self.assertMarkdownRenders(
            'Commit [83fb46b3b7ab8ad4316681fc4637c521da265f1d](#).',
            '<p>Commit <a href="#">83fb46b3b7ab8ad4316681fc4637c521da265f1d</a>.</p>',
        )

    # Base URL Tests
    def test_base_url(self):
        self.assertMarkdownRenders(
            'Issue #123.',
            '<p>Issue <a class="forge-link forge-issue" '
            'href="https://example.org/git/tmb/mdx-forge-links/issues/123" '
            'title="Issue tmb/mdx-forge-links #123">#123</a>.</p>',
            base_url='https://example.org/git',
        )


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
