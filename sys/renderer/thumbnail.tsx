import React from 'react';
import {AbsoluteFill, Img, staticFile} from 'remotion';

export const Thumbnail: React.FC<any> = ({image, text, title, badge, width, height, overlay_card = false}) => {
  const displayTitle = title || text || '';
  const isPortrait = height > width;

  return (
    <AbsoluteFill style={{background: '#FFFFFF', width, height}}>
      {image ? (
        <Img
          src={staticFile(image)}
          decoding="sync"
          style={{width: '100%', height: '100%', objectFit: isPortrait ? 'contain' : 'cover'}}
        />
      ) : null}
      {overlay_card || (!image && displayTitle) ? (
        <>
          {image ? (
            <AbsoluteFill style={{background: 'linear-gradient(0deg, #0F172Aee, transparent 80%)'}} />
          ) : null}
          {badge ? (
            <div
              style={{
                position: 'absolute',
                left: '6%',
                bottom: isPortrait ? '34%' : '38%',
                background: '#EF4444',
                color: '#FFFFFF',
                padding: isPortrait ? '8px 20px' : '10px 26px',
                borderRadius: 8,
                fontFamily: 'Arial',
                fontWeight: 800,
                fontSize: isPortrait ? 34 : 40,
                letterSpacing: '0.05em',
                textTransform: 'uppercase',
                boxShadow: '0 4px 12px rgba(0,0,0,0.5)',
              }}
            >
              {badge}
            </div>
          ) : null}
          {displayTitle ? (
            <div
              style={{
                position: 'absolute',
                left: '6%',
                bottom: '20%',
                width: '84%',
                fontFamily: 'Arial',
                fontWeight: 900,
                fontSize: isPortrait ? 90 : 120,
                lineHeight: 1.12,
                color: '#FACC15',
                textShadow: '0 4px 12px #000, 0 2px 4px #000',
                textTransform: 'uppercase',
                wordBreak: 'break-word',
              }}
            >
              {displayTitle}
            </div>
          ) : null}
        </>
      ) : null}
    </AbsoluteFill>
  );
};
