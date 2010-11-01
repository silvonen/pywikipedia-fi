#!/usr/bin/python
# -*- coding: utf-8  -*-
"""
Categorize people according to their year of birth and death.

The following parameters are supported:

&params;

-dry              If given, doesn't do any real changes, but only shows
                  what would have been changed.

All other parameters will be regarded as part of the title of a single page,
and the bot will only work on that single page.
"""
__version__ = '$Id$'
import wikipedia as pywikibot
import catlib, pagegenerators, re

# This is required for the text that is shown when you run this script
# with the parameter -help.
docuReplacements = {
    '&params;': pagegenerators.parameterHelp
}

class BirthCatBot:
    # Edit summary message that should be used.
    # NOTE: Put a good description here, and add translations, if possible!
    msg = {
        'fi': u'Botti lisäsi: %s',
    }

    msgNewCat = {
        'fi': u'Botti loi uuden luokan',
    }

    # TODO: Implement BC years
    dateFormat = {
        'fi': ur'(?:\[*\d+\.\s+\S+kuuta\]*,?\s+)?\[*(\d+)\]*',
        }
    
    birthDeathCats = {
        'fi': {
            u'Vuonna %s syntyneet' : {
                'templates' :{
                    u'Syntymäaika ja ikä': 3,
                    u'Syntymä- ja kuolinaika': 3,
                    u'Kuolinaika ja ikä': 3,
                    },
                're': [
                    re.compile(ur'syntynyt\s*=\s*' + dateFormat['fi']),
                    re.compile(ur"'''[^)]*(?:\bs\.\s+|,\s+|\(|(?<!&ndash);\s+)" + dateFormat['fi']),
                    ],
                'newcat': lambda yr: u'{{Syntymävuosiluokka|%s|%s}}\n\n[[en:Category:%s births]]' % (yr[:-1], yr[-1], yr)
                },
            u'Vuonna %s kuolleet' : {
                'templates' :{
                    u'Syntymä- ja kuolinaika': 6,
                    u'Kuolinaika ja ikä': 6,
                    },
                're': [
                    re.compile(ur'kuollut\s*=\s*' + dateFormat['fi']),
                    re.compile(ur"'''[^()]*\((?:[^)]|\([^)]*\))*(?:\bk\.\s+|(?:[–—-]|&ndash;)\s*)" + dateFormat['fi']),
                    ],
                'newcat': lambda yr: u'{{Kuolinvuosiluokka|%s|%s}}\n\n[[en:Category:%s deaths]]' % (yr[:-1], yr[-1], yr)
                }
            }
        }
    
    def __init__(self, generator, dry):
        """
        Constructor. Parameters:
            * generator - The page generator that determines on which pages
                          to work on.
            * dry       - If True, doesn't do any real changes, but only shows
                          what would have been changed.
        """
        self.generator = generator
        self.dry = dry
        self.lang = pywikibot.getSite().lang
        
        # Get the correct localized parameters
        self.site = pywikibot.getSite()
        self.summary = pywikibot.translate(self.site, self.msg)
        self.summaryNewCat = pywikibot.translate(self.site, self.msgNewCat)
        self.bdCats = pywikibot.translate(self.site, self.birthDeathCats)

        self.defaultSortMatcher = None        
        defaultSortLabels = self.site.getmagicwords('defaultsort')
        if defaultSortLabels:
            self.defaultSortMatcher = re.compile('\{\{(' + '|'.join(defaultSortLabels) + ')')
        
    def run(self):
        try:
            for page in self.generator:
                self.treat(page)
        except KeyboardInterrupt:
            pywikibot.output('\nQuitting program...')

    def getSortKey(self, cats, text):
        if not self.defaultSortMatcher or not cats or self.defaultSortMatcher.search(text):
            sortKey = None
        else:
            sortKey = cats[0].sortKey
            if sortKey and sortKey[0] in '* ':
                sortKey = None

        return sortKey
       
    def treat(self, page):
        """
        Adds the page to the appropriate birth and death year categories.
        """
        pywikibot.output(u"Processing page %s..." % page.title(asLink=True))
        text = self.load(page)
        if not text:
            return
        
        cats = page.categories()
        addCats = []
        newCatContent = {}
        foundTemplates = False
        for tmpl, params in page.templatesWithParams():
            numParams = filter(lambda s: s.isdigit(), params) # Filter out birthplace fields
            for bdCat, bdCatInfo in self.bdCats.iteritems():
                if tmpl in bdCatInfo['templates']:
                    pywikibot.output(u'Found template {{%s|%s}}' % (tmpl, u'|'.join(params)))
                    foundTemplates = True
                    try:
                        year = numParams[bdCatInfo['templates'][tmpl] - 1].strip()
                    except IndexError:
                        continue
                    sortKey = self.getSortKey(cats, text)
                    newCat = catlib.Category(self.site, bdCat % year, sortKey=sortKey)
                    if newCat in cats or newCat in addCats:
                        pywikibot.output(u"%s is already in %s." % (page.title(), newCat.title()))
                    else:
                        addCats.append(newCat)
                        newCatContent[newCat.title()] = bdCatInfo['newcat'](year)

        if not addCats and not foundTemplates:
            for bdCat, bdCatInfo in self.bdCats.iteritems():
                for reMatcher in bdCatInfo['re']:
                    match = reMatcher.search(text)
                    if match:
                        year = match.group(1)
                        pywikibot.output(u'Found %s in %s' % (year, match.group(0)))
                        sortKey = self.getSortKey(cats, text)
                        newCat = catlib.Category(self.site, bdCat % year, sortKey=sortKey)
                        if newCat in cats or newCat in addCats:
                            pywikibot.output(u"%s is already in %s." % (page.title(), newCat.title()))
                        else:
                            addCats.append(newCat)
                            newCatContent[newCat.title()] = bdCatInfo['newcat'](year)

        if addCats:
            cats.extend(addCats)
            text = pywikibot.replaceCategoryLinks(text, cats)
            summary = self.summary % ', '.join(map(lambda c: c.title(asLink=True), addCats))
            if not self.save(text, page, summary):
                pywikibot.output(u'Page %s not saved.' % page.title(asLink=True))
                return
            for cat in addCats:
                if not cat.exists():
                    pywikibot.output(u'%s should be created.' % (cat.title()))
                    if not self.save(newCatContent[cat.title()], cat, self.summaryNewCat, minorEdit=False):
                        pywikibot.output(u'%s not created.' % cat.title(asLink=True))

    def load(self, page):
        """
        Loads the given page, does some changes, and saves it.
        """
        try:
            # Load the page
            text = page.get()
        except pywikibot.NoPage:
            pywikibot.output(u"Page %s does not exist; skipping."
                             % page.title(asLink=True))
        except pywikibot.IsRedirectPage:
            pywikibot.output(u"Page %s is a redirect; skipping."
                             % page.title(asLink=True))
        else:
            return text
        return None

    def save(self, text, page, comment, minorEdit=True, botflag=True):
        # only save if something was changed
        try:
            oldText = page.get()
        except pywikibot.NoPage:
            oldText = ""
        if text != oldText:
            # Show the title of the page we're working on.
            # Highlight the title in purple.
            pywikibot.output(u"\n\n>>> \03{lightpurple}%s\03{default} <<<"
                             % page.title())
            # show what was changed
            pywikibot.showDiff(oldText, text)
            pywikibot.output(u'Comment: %s' %comment)
            if not self.dry:
                choice = pywikibot.inputChoice(
                    u'Do you want to accept these changes?',
                    ['Yes', 'No'], ['y', 'N'], 'N')
                if choice == 'y':
                    try:
                        # Save the page
                        page.put(text, comment=comment,
                                 minorEdit=minorEdit, botflag=botflag)
                    except pywikibot.LockedPage:
                        pywikibot.output(u"Page %s is locked; skipping."
                                         % page.title(asLink=True))
                    except pywikibot.EditConflict:
                        pywikibot.output(
                            u'Skipping %s because of edit conflict'
                            % (page.title()))
                    except pywikibot.SpamfilterError, error:
                        pywikibot.output(u'Cannot change %s because of spam blacklist entry %s'
                            % (page.title(), error.url))
                    else:
                        return True
        return False

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

    # Parse command line arguments
    for arg in pywikibot.handleArgs():
        if arg.startswith("-dry"):
            dry = True
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
        bot = BirthCatBot(gen, dry)
        bot.run()
    else:
        pywikibot.showHelp()

if __name__ == "__main__":
    try:
        main()
    finally:
        pywikibot.stopme()
