#!/usr/bin/python
# -*- coding: utf-8  -*-
"""
Add redirects from scientific names to articles on living organisms.

The following parameters are supported:

&params;

-all              Work on all pages that use a taxobox template

-always           Don't prompt you for each redirect page to be added

-dry              If given, doesn't do any real changes, but only shows
                  what would have been changed.

All other parameters will be regarded as part of the title of a single page,
and the bot will only work on that single page.
"""
import pywikibot
from pywikibot import pagegenerators
import os.path, pickle, re

# This is required for the text that is shown when you run this script
# with the parameter -help.
docuReplacements = {
    '&params;': pagegenerators.parameterHelp
}

class SciNameBot:
    # Edit summary message that should be used.
    # NOTE: Put a good description here, and add translations, if possible!
    msg = {
        'en': u'Robot: Adding a scientific name for %s',
        'fi': u'Botti lisäsi eliön %s tieteellisen nimen',
    }

    taxoboxTemplates = {
        'fi': [ u'Taksonomia/eläimet', u'Taksonomia/kasvit', u'Taksonomia/sienet' ]
    }

    sciNameParameters = {
        'fi': [ u'kaksiosainen', u'kolmiosainen' ]
    }

    cacheFilename = os.path.join(u'cache', u'sciname')
    
    def __init__(self, generator, dry, always):
        """
        Constructor. Parameters:
            * generator - The page generator that determines on which pages
                          to work on.
            * dry       - If True, doesn't do any real changes, but only shows
                          what would have been changed.
            * always    - If True, don't prompt for each redirect page.
        """
        self.generator = generator
        self.dry = dry
        self.always = always
        self.lang = pywikibot.getSite().lang
        
        # Set the edit summary message
        self.summary = pywikibot.translate(pywikibot.getSite(), self.msg)
        self.templates = pywikibot.translate(pywikibot.getSite(), self.taxoboxTemplates)
        self.templateParameters = pywikibot.translate(pywikibot.getSite(), self.sciNameParameters)

        # Initialize the cache
        try:
            self.cache = pickle.load(file(self.cacheFilename, 'rb'))
        except:
            self.cache = {}
        if not self.lang in self.cache:
            self.cache[self.lang] = {}

    def getSciName(self, params):
        for param in params:
            for sciNameParam in self.templateParameters:
                m = re.search(u'^\s*%s\s*=([^<{]*)' % sciNameParam, param)
                if m:
                    sciname = m.group(1).strip()
                    if sciname:
                        return sciname
        return None
        
    def run(self):
        try:
            for page in self.generator:
                self.treat(page)
        except KeyboardInterrupt:
            pywikibot.output('\nQuitting program...')

        if not self.dry:
            pickle.dump(self.cache, file(self.cacheFilename, 'wb'))

    def treat(self, page):
        """
        Adds a redirect from scientific name to page if it does not exist.
        """
        pywikibot.output(u"Processing page %s..." % page.title(asLink=True))
        for tmpl, params in page.templatesWithParams():
            if tmpl.title(withNamespace=False) in self.templates:
                sciName = self.getSciName(params)
                if not sciName:
                    pywikibot.output(u"Scientific name not found; skipping.")
                elif sciName.find(u"''") != -1:
                    pywikibot.output(u"Text formatting in scientific name; skipping.")
                elif sciName in self.cache[self.lang]:
                    pywikibot.output(u'"%s" found in cache; skipping.' % sciName)
                else:
                    redirPage = pywikibot.Page(pywikibot.getSite(), sciName)
                    if redirPage.exists():
                        pywikibot.output(u"Page %s exists; skipping." % redirPage.title(asLink=True))
                        self.cache[self.lang][sciName] = page.title()
                    else:
                        pywikibot.output(u"Creating redirect page %s." % redirPage.title(asLink=True))
                        text = u'#%s %s' % (pywikibot.getSite().redirect(True), page.title(asLink=True))
                        if not self.dry:
                            if self.always:
                                choice = 'y'
                            else:
                                choice = pywikibot.inputChoice(u'Do you want to create this page?', ['Yes', 'No'], ['y', 'N'], 'N')
                            if choice == 'y':
                                try:
                                    # Save the page
                                    redirPage.put(text, comment=self.summary % page.title(asLink=True))
                                except pywikibot.LockedPage:
                                    pywikibot.output(u"Page %s is locked; skipping." % redirPage.title(asLink=True))
                                except pywikibot.EditConflict:
                                    pywikibot.output(u'Skipping %s because of edit conflict' % (redirPage.title()))
                                except pywikibot.SpamfilterError, error:
                                    pywikibot.output(u'Cannot change %s because of spam blacklist entry %s' % (redirPage.title(), error.url))
                                else:
                                    self.cache[self.lang][sciName] = page.title()

def main():
    # This factory is responsible for processing command line arguments
    # that are also used by other scripts and that determine on which pages
    # to work on.
    genFactory = pagegenerators.GeneratorFactory()
    # The generator gives the pages that should be worked upon.
    gen = None
    # This temporary array is used to read the page title if one single
    # page to work on is specified by the arguments.
    pageTitleParts = []
    # If dry is True, doesn't do any real changes, but only show
    # what would have been changed.
    dry = False
    # If always is True, don't confirm changes.
    always = False

    # Parse command line arguments
    for arg in pywikibot.handleArgs():
        if arg.startswith("-dry"):
            dry = True
        elif arg.startswith("-always"):
            always = True
        elif arg.startswith("-all"):
            genFactory.handleArg('-namespace:0')
            for tmpl in pywikibot.translate(pywikibot.getSite(), SciNameBot.taxoboxTemplates):
                genFactory.handleArg('-transcludes:%s' % tmpl)
        else:
            # check if a standard argument like
            # -start:XYZ or -ref:Asdf was given.
            if not genFactory.handleArg(arg):
                pageTitleParts.append(arg)

    if pageTitleParts != []:
        # We will only work on a single page.
        pageTitle = ' '.join(pageTitleParts)
        page = pywikibot.Page(pywikibot.getSite(), pageTitle)
        gen = iter([page])

    if not gen:
        gen = genFactory.getCombinedGenerator()
    if gen:
        # The preloading generator is responsible for downloading multiple
        # pages from the wiki simultaneously.
        gen = pagegenerators.PreloadingGenerator(gen)
        bot = SciNameBot(gen, dry, always)
        bot.run()
    else:
        pywikibot.showHelp()

if __name__ == "__main__":
    try:
        main()
    finally:
        pywikibot.stopme()
