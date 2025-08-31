/**
 * ABOUT
 * 
 * This is a Twitter NO-API/Dependency-Free follower sniffer and auto-blocker.
 * 
 * This function performs automatic bulk blocking with NO-API
 * and NO-external-dependencies to run. You must run this snippet
 * directly on your Console, it will sniff your followers list
 * search for previous given keywords, if found on username or description,
 * the user will be automatically blocked.
 * 
 * GETTING STARTED:
 * 
 * 1. Go to your twitter profile webpage using a desktop navigator, preferentially
 * Chrome. Now go to your "followers" page: https://twitter.com/<username>/followers
 * 
 * 2. On your followers page you must open your browser inspector, go to
 * the "console" and paste this entire code. Be sure to be logged on twitter.
 * 
 * Usage:
 * 
 * Now you must call the function passing the parameters to the seeker.
 * Use the same console that you pasted the function to do it.
 * 
 * Example:
 * 
 * seekAndDestroy({ keywords: 'fizz' });
 * 
 * The function bellow will search for every user that has the keyword "fizz"
 * on the name or profile, and will list them. It wont automatically block since
 * the dryrun options is true by default. To block all the users based on your criteria
 * you msut remove the dryrun security key:
 * 
 * seekAndDestroy({ keywords: 'fizz', dryrun: false });
 * 
 * Now all the users that match your criteria (keywords) will be automatically blocked.
 * 
 * OPTIONS: 
 * 
 * {
 *    keywords: [ "example" ],
 *    strategy: "some",
 *    dryrun: true 
 * } 
 * 
 * keywords: string[]
 * All the words to search for when deciding who's to block
 * 
 * strategy: some|every
 * How to compare keywords.
 * "some": blocks the user if match at least on keyword of keywords list
 * "every": blocks the user only when matching all keywords of keywords list
 * 
 * dryrun
 * Do not REALLY block users. This is true by default for security reasons.
 * THis options is also useful to get just a list of users that were sniffed.
 * 
 * NOTE:
 * 
 * The script will slowly scan your users list automatically scrolling the page
 * and chacking user by user. This may take some time, go get a coffee :)
 * 
 * GETTING A REPORT:
 * 
 * When running the "seekAndDestroy" function you can stop the task and get a
 * report with all the users that matched your criteria. Just click on any
 * blank part of the current screen and press "q". A file will be automatically
 * download showing you all the users found that matched your query.
 * 
 * EXAMPLES:
 * 
 * Be sure to be on your "followers" page. Now...
 * 
 * Check all users that has the word "nazi" on the name/description:
 * seekAndDestroy({ keywords: 'nazi' });
 *
 * Check and automatically block all users that has the word "nazi" on the name/description:
 * seekAndDestroy({ keywords: 'nazi', dryrun: false });
 * 
 * Check all users that has both the words "nazi" and "lover" on the name/description
 * seekAndDestroy({ keywords: ['nazi', 'lover'], strategy: 'every' });
 * 
 * WARN!!!
 * 
 * This function is distributed with NO GUARANTEES. Use by you own risk. Make sure
 * that you know exactly what you are doing, or you may be in risk to accidentally 
 * block all your followers list. In case of doubt, prefer not to use.
 */
function seekAndDestroy(overrides = {}) {
  const blocked = [];
  const options = { keywords: [], dryrun: true, strategy: 'some', ...overrides };
  const { keywords, dryrun, strategy } = options;

  let locked = false;

  const block = (item, retries = 50) => {
    if (!retries) return;

    try {
      item.querySelector('[aria-haspopup=menu').click();
      
      const blockbtn = document.querySelector('[role=menuitem][data-testid=block]');
      if (!blockbtn) return block(item, --retries);
      blockbtn.click();
      
      const blockconfirmbtn = document.querySelector('[role=button][data-testid="confirmationSheetConfirm"]');
      if (!blockconfirmbtn) return block(item, --retries);
      
      if (!dryrun) {
        blockconfirmbtn.click();
      }

      document.querySelector('[data-testid=mask]').click();
    } catch {
      return block(item, --retries);
    }
  };  
  
  const running = setInterval(() => {
    if (locked) return;

    const found = document.querySelectorAll('[data-testid=cellInnerDiv]') || [];
    const normalize = str => str.toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "");
    let blockedCount = blocked.length;
    locked = true;
    
    found.forEach(item => {
      const userUrl = item.querySelector('a')?.href;
      const mustBlock = keywords[strategy](word => normalize(item.textContent || '').includes(normalize(word)));

      if (mustBlock && !blocked.includes(userUrl)) {
        block(item);
        blocked.push(userUrl);
        console.log(`💣 ${userUrl} [dry run ${dryrun}]`);
      }
    });

    const backwardScroll = document.body.scrollHeight - window.innerHeight;
    const scrollIndex = blockedCount === block.length ? document.body.scrollHeight : (backwardScroll > 0 ? backwardScroll : 0);
    
    console.log('Scrolled to new position ', scrollIndex);
    window.scrollTo(0, scrollIndex);
    locked = false;
  }, 5000);

  const onQuit = e => {
    if (e.key === 'q') {
      clearInterval(running);
      
      const filename = `seek-and-destroy-${Date.now()}.txt`;
      const text = blocked.join('\n');
      const a = document.createElement('a');

      a.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(text));
      a.setAttribute('download', filename);    
      a.click();
      a.remove();

      removeEventListener(onQuit);
    }
  };

  window.addEventListener('keyup', onQuit);
}