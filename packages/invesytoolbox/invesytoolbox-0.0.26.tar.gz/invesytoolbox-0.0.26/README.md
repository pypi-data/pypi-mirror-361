# invesytoolbox

A set of useful tools, created for my own convenience.

Why "invesy"? Invesy (from German **In**halts**ve**rwaltungs**sy**stem == content management system) is a closed source cms I created with Thomas Macher. It's only used in-house, that's why we didn't bother making it open source.

Invesy runs on Zope, so most of the individual website's logic runs in restricted Python. That's one reason for this toolbox: providing a set of useful functions in one single package which can be allowed in our restricted Python environment without having to allow a long list of external packages. Also some packages, while being importable, contain functions or methods not usable in restricted Python (like bs4's prettify).

That's also why all date and time functions also take into account the old DateTime (as opposed to datetime) package, on which Zope is still relying upon heavily.

## Links

- The documentation can be found here: [rastaf.gitlab.io/invesytoolbox](https://rastaf.gitlab.io/invesytoolbox/).
- The project history can be found here: [HISTORY.md](https://gitlab.com/Rastaf/invesytoolbox/blob/master/HISTORY.md)